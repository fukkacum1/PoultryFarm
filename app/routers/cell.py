from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date
from app.db.session_maker import db
from app.db.models import Cell
from config import settings

router = APIRouter()

@router.get("/eggs/summary")
async def get_eggs_summary(
    start_date: date = Query(..., description="Дата начала диапазона (включительно)"),
    end_date: date = Query(..., description="Дата конца диапазона (включительно)"),
    session: AsyncSession = Depends(db.get_db)
):
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="start_date не может быть больше end_date")

    query = (
        select(
            func.sum(Cell.number_of_eggs).label("total_eggs")
        )
        .where(
            and_(
                Cell.date >= start_date,
                Cell.date <= end_date
            )
        )
    )

    result = await session.execute(query)
    total_eggs = result.scalar_one_or_none() or 0
    total_cost = total_eggs * settings.EGG_PRICE

    return {
        "start_date": start_date,
        "end_date": end_date,
        "total_eggs": total_eggs,
        "total_cost": total_cost
    }

