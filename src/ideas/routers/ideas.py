from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..database import get_db
from ..models import Idea, Message, IdeaStatus, MessageType
from ..schemas import (
    IdeaCreate, IdeaUpdate, IdeaResponse, IdeaWithMessages,
    MessageCreate, MessageResponse, StatusChangeResponse
)

router = APIRouter()


def add_system_event(idea: Idea, content: str, session: AsyncSession):
    message = Message(
        idea_id=idea.id,
        type=MessageType.SYSTEM_EVENT,
        content=content
    )
    session.add(message)


@router.post("", response_model=IdeaResponse, status_code=status.HTTP_201_CREATED)
async def create_idea(idea_data: IdeaCreate, db: AsyncSession = Depends(get_db)):
    idea = Idea(content=idea_data.content)
    db.add(idea)
    await db.commit()
    await db.refresh(idea)
    
    add_system_event(idea, "Idea created", db)
    await db.commit()
    
    return idea


@router.get("", response_model=list[IdeaResponse])
async def list_ideas(
    status_filter: IdeaStatus | None = None,
    db: AsyncSession = Depends(get_db)
):
    query = select(Idea)
    if status_filter:
        query = query.where(Idea.status == status_filter)
    query = query.order_by(Idea.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/{idea_id}", response_model=IdeaWithMessages)
async def get_idea(idea_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Idea)
        .options(selectinload(Idea.messages))
        .where(Idea.id == idea_id)
    )
    idea = result.scalar_one_or_none()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    return idea


@router.put("/{idea_id}", response_model=IdeaResponse)
async def update_idea(
    idea_id: int,
    idea_data: IdeaUpdate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalar_one_or_none()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    if idea_data.content is not None:
        old_content = idea.content[:50] + "..." if len(idea.content) > 50 else idea.content
        idea.content = idea_data.content
        add_system_event(idea, f"Content updated from: {old_content}", db)
    
    await db.commit()
    await db.refresh(idea)
    return idea


@router.post("/{idea_id}/execute", response_model=StatusChangeResponse)
async def execute_idea(idea_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalar_one_or_none()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    if idea.status != IdeaStatus.DRAFT:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot execute idea in {idea.status.value} status"
        )
    
    old_status = idea.status
    idea.status = IdeaStatus.PENDING
    add_system_event(idea, f"Execution requested: {old_status.value} -> {idea.status.value}", db)
    
    await db.commit()
    
    return StatusChangeResponse(
        id=idea.id,
        old_status=old_status,
        new_status=idea.status,
        message="Idea marked for execution"
    )


@router.post("/{idea_id}/cancel", response_model=StatusChangeResponse)
async def cancel_idea(idea_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalar_one_or_none()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    terminal_statuses = [IdeaStatus.COMPLETED, IdeaStatus.FAILED, IdeaStatus.CANCELLED]
    if idea.status in terminal_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel idea in {idea.status.value} status"
        )
    
    old_status = idea.status
    idea.status = IdeaStatus.CANCELLED
    add_system_event(idea, f"Execution cancelled: {old_status.value} -> {idea.status.value}", db)
    
    await db.commit()
    
    return StatusChangeResponse(
        id=idea.id,
        old_status=old_status,
        new_status=idea.status,
        message="Idea cancelled"
    )


@router.post("/{idea_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def add_message(
    idea_id: int,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalar_one_or_none()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    message = Message(
        idea_id=idea.id,
        type=MessageType.USER_INPUT,
        content=message_data.content
    )
    db.add(message)
    
    # If waiting for user, transition to waiting for agent
    if idea.status == IdeaStatus.WAITING_USER:
        idea.status = IdeaStatus.WAITING_AGENT
        add_system_event(idea, "User provided instruction, waiting for agent to continue", db)
    
    await db.commit()
    await db.refresh(message)
    
    return message


@router.get("/{idea_id}/messages", response_model=list[MessageResponse])
async def get_messages(idea_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Idea).where(Idea.id == idea_id))
    idea = result.scalar_one_or_none()
    
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    
    result = await db.execute(
        select(Message)
        .where(Message.idea_id == idea_id)
        .order_by(Message.created_at)
    )
    return result.scalars().all()
