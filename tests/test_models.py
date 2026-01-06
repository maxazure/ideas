import pytest
from sqlalchemy import select
from ideas.models import Idea, Message, IdeaStatus, MessageType


class TestIdeaModel:
    @pytest.mark.asyncio
    async def test_create_idea_with_default_status(self, db_session):
        # given: a new idea with content
        idea = Idea(content="Test idea content")
        
        # when: saved to database
        db_session.add(idea)
        await db_session.commit()
        await db_session.refresh(idea)
        
        # then: idea has default draft status
        assert idea.id is not None
        assert idea.content == "Test idea content"
        assert idea.status == IdeaStatus.DRAFT
        assert idea.created_at is not None
        assert idea.updated_at is not None

    @pytest.mark.asyncio
    async def test_idea_status_transitions(self, db_session):
        # given: an idea in draft status
        idea = Idea(content="Test idea")
        db_session.add(idea)
        await db_session.commit()
        
        # when: status changes to pending
        idea.status = IdeaStatus.PENDING
        await db_session.commit()
        await db_session.refresh(idea)
        
        # then: status is updated
        assert idea.status == IdeaStatus.PENDING

    @pytest.mark.asyncio
    async def test_idea_with_messages(self, db_session):
        # given: an idea
        idea = Idea(content="Test idea")
        db_session.add(idea)
        await db_session.commit()
        
        # when: messages are added
        message1 = Message(
            idea_id=idea.id,
            type=MessageType.USER_INPUT,
            content="User instruction"
        )
        message2 = Message(
            idea_id=idea.id,
            type=MessageType.AGENT_FEEDBACK,
            content="Agent response"
        )
        db_session.add_all([message1, message2])
        await db_session.commit()
        
        # then: messages are linked to idea
        await db_session.refresh(idea)
        result = await db_session.execute(
            select(Message).where(Message.idea_id == idea.id)
        )
        messages = result.scalars().all()
        assert len(messages) == 2


class TestMessageModel:
    @pytest.mark.asyncio
    async def test_create_message_types(self, db_session):
        # given: an idea
        idea = Idea(content="Test idea")
        db_session.add(idea)
        await db_session.commit()
        
        # when: different message types are created
        for msg_type in MessageType:
            message = Message(
                idea_id=idea.id,
                type=msg_type,
                content=f"Content for {msg_type.value}"
            )
            db_session.add(message)
        await db_session.commit()
        
        # then: all message types are valid
        result = await db_session.execute(
            select(Message).where(Message.idea_id == idea.id)
        )
        messages = result.scalars().all()
        assert len(messages) == len(MessageType)
