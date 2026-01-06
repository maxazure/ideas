"""SQLAlchemy models for the Idea Execution Loop System."""
import enum
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import String, Text, Enum, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class IdeaStatus(str, enum.Enum):
    """Idea status enumeration."""
    DRAFT = "draft"               # 草稿（仅记录）
    PENDING = "pending"           # 待执行
    CLAIMED = "claimed"           # 已被 Agent 领取
    EXECUTING = "executing"       # 执行中
    WAITING_USER = "waiting_user" # 等待用户指示
    WAITING_AGENT = "waiting_agent" # 等待 Agent 继续
    COMPLETED = "completed"       # 已完成
    FAILED = "failed"             # 已失败
    CANCELLED = "cancelled"       # 已取消


class MessageType(str, enum.Enum):
    """Message type enumeration."""
    USER_INPUT = "user_input"       # 用户追加的说明、评论、指示
    AGENT_FEEDBACK = "agent_feedback"  # Agent 的执行进度、结果、问题
    SYSTEM_EVENT = "system_event"   # 系统自动记录的状态变化


def utc_now() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(timezone.utc)


class Idea(Base):
    """Idea model - the core business object of the system."""
    
    __tablename__ = "ideas"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[IdeaStatus] = mapped_column(
        Enum(IdeaStatus),
        default=IdeaStatus.DRAFT,
        nullable=False
    )
    agent_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False
    )
    
    # Relationship to messages (thread)
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="idea",
        cascade="all, delete-orphan",
        order_by="Message.created_at"
    )
    
    def __repr__(self) -> str:
        return f"<Idea(id={self.id}, status={self.status.value})>"


class Message(Base):
    """Message model - represents events in an idea's thread."""
    
    __tablename__ = "messages"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    idea_id: Mapped[int] = mapped_column(ForeignKey("ideas.id"), nullable=False)
    type: Mapped[MessageType] = mapped_column(
        Enum(MessageType),
        nullable=False
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False
    )
    
    # Relationship to idea
    idea: Mapped["Idea"] = relationship("Idea", back_populates="messages")
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, type={self.type.value}, idea_id={self.idea_id})>"
