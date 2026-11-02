"""KindBite — Notification service"""
from __future__ import annotations
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Notification


async def create_notification(
    db: AsyncSession,
    user_id: str,
    title: str,
    body: str,
    type: Optional[str] = None,
    related_id: Optional[str] = None,
) -> Notification:
    n = Notification(
        user_id=user_id,
        title=title,
        body=body,
        type=type,
        related_id=related_id,
    )
    db.add(n)
    return n
