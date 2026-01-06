from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models import Idea, Message, IdeaStatus, MessageType
from ..schemas import (
    IdeaResponse, AgentClaimRequest, AgentFeedbackRequest,
    AgentAskRequest, AgentCompleteRequest, AgentFailRequest,
    StatusChangeResponse
)

router = APIRouter()


def add_system_event(idea: Idea, content: str, session: AsyncSession):
    message = Message(
        idea_id=idea.id,
        type=MessageType.SYSTEM_EVENT,
        content=content
    )
    session.add(message)


@router.get("/poll", response_model=list[IdeaResponse])
async def poll_tasks(db: AsyncSession = Depends(get_db)):
    # Return ideas that are pending or waiting for agent
    pollable_statuses = [IdeaStatus.PENDING, IdeaStatus.WAITING_AGENT]
    result = await db.execute(
        select(Idea)
        .where(Idea.status.in_(pollable_statuses))
        .order_by(Idea.updated_at)
    )
    return result.scalars().all()


@router.post("/claim/{idea_id}", response_model=StatusChangeResponse)
async def claim_task(
    idea_id: int,
    claim_data: AgentClaimRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalar_one_or_none()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    if idea.status != IdeaStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot claim idea in {idea.status.value} status"
        )
    
    old_status = idea.status
    idea.status = IdeaStatus.CLAIMED
    idea.agent_id = claim_data.agent_id
    add_system_event(idea, f"Claimed by agent: {claim_data.agent_id}", db)
    
    await db.commit()
    
    return StatusChangeResponse(
        id=idea.id,
        old_status=old_status,
        new_status=idea.status,
        message=f"Task claimed by agent {claim_data.agent_id}"
    )


@router.post("/start/{idea_id}", response_model=StatusChangeResponse)
async def start_execution(
    idea_id: int,
    claim_data: AgentClaimRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalar_one_or_none()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    valid_statuses = [IdeaStatus.CLAIMED, IdeaStatus.WAITING_AGENT]
    if idea.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start execution for idea in {idea.status.value} status"
        )
    
    if idea.agent_id != claim_data.agent_id:
        raise HTTPException(status_code=403, detail="Not authorized agent")
    
    old_status = idea.status
    idea.status = IdeaStatus.EXECUTING
    add_system_event(idea, f"Execution started by agent: {claim_data.agent_id}", db)
    
    await db.commit()
    
    return StatusChangeResponse(
        id=idea.id,
        old_status=old_status,
        new_status=idea.status,
        message="Execution started"
    )


@router.post("/feedback/{idea_id}", response_model=StatusChangeResponse)
async def submit_feedback(
    idea_id: int,
    feedback_data: AgentFeedbackRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalar_one_or_none()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    if idea.status != IdeaStatus.EXECUTING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot submit feedback for idea in {idea.status.value} status"
        )
    
    if idea.agent_id != feedback_data.agent_id:
        raise HTTPException(status_code=403, detail="Not authorized agent")
    
    message = Message(
        idea_id=idea.id,
        type=MessageType.AGENT_FEEDBACK,
        content=feedback_data.content
    )
    db.add(message)
    await db.commit()
    
    return StatusChangeResponse(
        id=idea.id,
        old_status=idea.status,
        new_status=idea.status,
        message="Feedback recorded"
    )


@router.post("/ask/{idea_id}", response_model=StatusChangeResponse)
async def ask_user(
    idea_id: int,
    ask_data: AgentAskRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalar_one_or_none()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    if idea.status != IdeaStatus.EXECUTING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot ask user for idea in {idea.status.value} status"
        )
    
    if idea.agent_id != ask_data.agent_id:
        raise HTTPException(status_code=403, detail="Not authorized agent")
    
    old_status = idea.status
    idea.status = IdeaStatus.WAITING_USER
    
    message = Message(
        idea_id=idea.id,
        type=MessageType.AGENT_FEEDBACK,
        content=f"[Question] {ask_data.question}"
    )
    db.add(message)
    add_system_event(idea, "Agent requested user instruction", db)
    
    await db.commit()
    
    return StatusChangeResponse(
        id=idea.id,
        old_status=old_status,
        new_status=idea.status,
        message="Waiting for user instruction"
    )


@router.post("/complete/{idea_id}", response_model=StatusChangeResponse)
async def complete_task(
    idea_id: int,
    complete_data: AgentCompleteRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalar_one_or_none()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    if idea.status != IdeaStatus.EXECUTING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot complete idea in {idea.status.value} status"
        )
    
    if idea.agent_id != complete_data.agent_id:
        raise HTTPException(status_code=403, detail="Not authorized agent")
    
    old_status = idea.status
    idea.status = IdeaStatus.COMPLETED
    
    summary = complete_data.summary or "Task completed successfully"
    message = Message(
        idea_id=idea.id,
        type=MessageType.AGENT_FEEDBACK,
        content=f"[Completed] {summary}"
    )
    db.add(message)
    add_system_event(idea, "Task completed", db)
    
    await db.commit()
    
    return StatusChangeResponse(
        id=idea.id,
        old_status=old_status,
        new_status=idea.status,
        message="Task completed"
    )


@router.post("/fail/{idea_id}", response_model=StatusChangeResponse)
async def fail_task(
    idea_id: int,
    fail_data: AgentFailRequest,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalar_one_or_none()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    if idea.status != IdeaStatus.EXECUTING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot fail idea in {idea.status.value} status"
        )
    
    if idea.agent_id != fail_data.agent_id:
        raise HTTPException(status_code=403, detail="Not authorized agent")
    
    old_status = idea.status
    idea.status = IdeaStatus.FAILED
    
    message = Message(
        idea_id=idea.id,
        type=MessageType.AGENT_FEEDBACK,
        content=f"[Failed] {fail_data.reason}"
    )
    db.add(message)
    add_system_event(idea, f"Task failed: {fail_data.reason}", db)
    
    await db.commit()
    
    return StatusChangeResponse(
        id=idea.id,
        old_status=old_status,
        new_status=idea.status,
        message="Task failed"
    )
