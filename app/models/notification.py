from __future__ import annotations
"""
====================================================================
  Project : Geply - AI Interview Platform
  Company : GEP Worldwide
  Author  : Prasanth Ragupathy <prasanth.ragupathy@gep.com>
  File    : notification.py
====================================================================
"""
"""
====================================================================
  Project : Geply - AI Interview Platform
  Company : GEP Worldwide
  Author  : Prasanth Ragupathy <prasanth.ragupathy@gep.com>
  File    : notification.py
  Purpose : Module in the Geply AI Interview Platform by Prasanth Ragupathy.
====================================================================
"""

from sqlalchemy import Boolean, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Notification(Base):
    """In-app notification for recruiters (bell icon with unread badge)."""

    __tablename__ = "notifications"

    recruiter_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    type: Mapped[str] = mapped_column(String(50), index=True)
    title: Mapped[str] = mapped_column(String(500), default="")
    message: Mapped[str] = mapped_column(Text, default="")
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
