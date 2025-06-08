from fastapi import APIRouter, Depends, Path
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.db.session_maker import db
from app.db.models import Cell, Worker, birds_in_cells

router = APIRouter()

@router.get("/{worker_id}/eggs")
async def get_eggs_by_worker(
    worker_id: int = Path(..., description="ID работника"),
    session: AsyncSession = Depends(db.get_db)
):
    query = (
        select(
            func.sum(Cell.number_of_eggs).label("total_eggs")
        )
        .where(Cell.worker_id == worker_id)
    )
    result = await session.execute(query)
    total_eggs = result.scalar_one_or_none() or 0

    return {
        "worker_id": worker_id,
        "total_eggs": total_eggs,
    }


@router.get("/birds_count/by_worker")
async def get_birds_count_by_worker(session: AsyncSession = Depends(db.get_db)):
    cell_alias = aliased(Cell)
    query = (
        select(
            Worker.id.label("worker_id"),
            func.count(func.distinct(birds_in_cells.c.bird_id)).label("birds_count")
        )
        .join(cell_alias, cell_alias.worker_id == Worker.id)
        .join(birds_in_cells, birds_in_cells.c.cell_id == cell_alias.id)
        .group_by(Worker.id)
    )

    result = await session.execute(query)
    rows = result.all()

    response = []
    for worker_id, birds_count in rows:
        response.append({
            "worker_id": worker_id,
            "birds_count": birds_count
        })

    return response