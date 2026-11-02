"""
KindBite — Sales endpoints (manual entry + CSV import)
"""
from __future__ import annotations
import csv
import io
import uuid
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_restaurant_or_admin
from app.db.session import get_db
from app.models import FoodItem, Restaurant, SalesRecord, User
from app.schemas.schemas import SalesRecordCreate, SalesRecordOut

router = APIRouter()

REQUIRED_CSV_COLUMNS = {"food_item_id", "date", "sold_quantity_kg"}


async def _get_restaurant(user: User, db: AsyncSession) -> Restaurant:
    r = await db.execute(select(Restaurant).where(Restaurant.owner_id == user.id))
    restaurant = r.scalar_one_or_none()
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant profile not found.")
    return restaurant


@router.post("", response_model=SalesRecordOut, status_code=201)
async def create_sales_record(
    payload: SalesRecordCreate,
    current_user: User = Depends(require_restaurant_or_admin),
    db: AsyncSession = Depends(get_db),
):
    restaurant = await _get_restaurant(current_user, db)

    # Validate food item belongs to this restaurant
    fi = await db.execute(
        select(FoodItem).where(
            FoodItem.id == payload.food_item_id,
            FoodItem.restaurant_id == restaurant.id,
        )
    )
    if not fi.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Food item not found in your restaurant.")

    record = SalesRecord(
        restaurant_id=restaurant.id,
        **payload.model_dump(),
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return SalesRecordOut.model_validate(record)


@router.get("", response_model=List[SalesRecordOut])
async def list_sales_records(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    food_item_id: Optional[str] = None,
    current_user: User = Depends(require_restaurant_or_admin),
    db: AsyncSession = Depends(get_db),
):
    restaurant = await _get_restaurant(current_user, db)
    q = select(SalesRecord).where(SalesRecord.restaurant_id == restaurant.id)
    if food_item_id:
        q = q.where(SalesRecord.food_item_id == food_item_id)
    q = q.order_by(SalesRecord.date.desc()).offset(skip).limit(limit)
    result = await db.execute(q)
    return [SalesRecordOut.model_validate(r) for r in result.scalars().all()]


@router.post("/import")
async def import_sales_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(require_restaurant_or_admin),
    db: AsyncSession = Depends(get_db),
):
    """Import sales records from a CSV file.
    Required columns: food_item_id, date, sold_quantity_kg
    Optional: prepared_quantity_kg, leftover_quantity_kg, revenue_inr, notes
    """
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV.")

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 10 MB).")

    text = content.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    
    if not reader.fieldnames:
        raise HTTPException(status_code=400, detail="CSV file is empty or has no headers.")
    
    missing = REQUIRED_CSV_COLUMNS - set(reader.fieldnames)
    if missing:
        raise HTTPException(
            status_code=422,
            detail=f"CSV missing required columns: {', '.join(missing)}",
        )

    restaurant = await _get_restaurant(current_user, db)
    batch_id = str(uuid.uuid4())[:8]
    imported, errors = 0, []

    for i, row in enumerate(reader, start=2):
        try:
            food_item_id = row["food_item_id"].strip()
            fi = await db.execute(
                select(FoodItem).where(
                    FoodItem.id == food_item_id,
                    FoodItem.restaurant_id == restaurant.id,
                )
            )
            if not fi.scalar_one_or_none():
                errors.append({"row": i, "error": f"Food item {food_item_id} not found."})
                continue

            sold_qty = float(row["sold_quantity_kg"])
            if sold_qty < 0:
                raise ValueError("sold_quantity_kg cannot be negative")

            record = SalesRecord(
                restaurant_id=restaurant.id,
                food_item_id=food_item_id,
                date=datetime.fromisoformat(row["date"].strip()),
                sold_quantity_kg=sold_qty,
                prepared_quantity_kg=float(row["prepared_quantity_kg"]) if row.get("prepared_quantity_kg") else None,
                leftover_quantity_kg=float(row["leftover_quantity_kg"]) if row.get("leftover_quantity_kg") else None,
                revenue_inr=float(row["revenue_inr"]) if row.get("revenue_inr") else None,
                notes=row.get("notes"),
                import_batch_id=batch_id,
            )
            db.add(record)
            imported += 1
        except (ValueError, KeyError) as e:
            errors.append({"row": i, "error": str(e)})

    await db.commit()
    return {
        "batch_id": batch_id,
        "imported": imported,
        "errors": errors,
        "message": f"Imported {imported} records with {len(errors)} errors.",
    }


@router.get("/summary")
async def sales_summary(
    current_user: User = Depends(require_restaurant_or_admin),
    db: AsyncSession = Depends(get_db),
):
    restaurant = await _get_restaurant(current_user, db)
    result = await db.execute(
        select(
            func.count(SalesRecord.id).label("total_records"),
            func.sum(SalesRecord.sold_quantity_kg).label("total_sold_kg"),
            func.sum(SalesRecord.prepared_quantity_kg).label("total_prepared_kg"),
            func.sum(SalesRecord.leftover_quantity_kg).label("total_leftover_kg"),
            func.sum(SalesRecord.revenue_inr).label("total_revenue_inr"),
        ).where(SalesRecord.restaurant_id == restaurant.id)
    )
    row = result.one()
    return {
        "total_records": row.total_records or 0,
        "total_sold_kg": float(row.total_sold_kg or 0),
        "total_prepared_kg": float(row.total_prepared_kg or 0),
        "total_leftover_kg": float(row.total_leftover_kg or 0),
        "total_revenue_inr": float(row.total_revenue_inr or 0),
    }
