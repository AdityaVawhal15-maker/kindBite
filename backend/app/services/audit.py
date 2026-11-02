"""KindBite — Audit service"""
from __future__ import annotations
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AuditLog


async def record_audit(
    db: AsyncSession,
    action: str,
    actor_id: Optional[str] = None,
    resource_type: Optional[str] = None,
    resource_id: Optional[str] = None,
    details: Optional[dict] = None,
    ip_address: Optional[str] = None,
) -> None:
    log = AuditLog(
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        details=details,
        ip_address=ip_address,
    )
    db.add(log)
    # Don't commit here — let the calling context commit
