from fastapi import APIRouter, Depends, HTTPException, Path, Body
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import JSONResponse
from loguru import logger

from app.db.session_maker import db
from app.db.dao import BirdDao
from app.schemas.bird import BirdMaxEggsResponse, BirdCreate

router = APIRouter()

def get_dao(db_session: AsyncSession = Depends(db.get_db)) -> BirdDao:
    return BirdDao(db_session)

@router.post(
    path="/add_bird",
    summary="Добавление курицы",
    responses={
        200: {"description": "Курица успешно добавлена"},
        400: {"description": "Некорректные данные"},
        500: {"description": "Ошибка сервера"}
    }
)
async def add_bird(
        bird_data: BirdCreate = Body(),
        db: AsyncSession = Depends(db.get_db_with_commit)
) -> JSONResponse:
    try:
        new_bird = await BirdDao(db).add(values=BirdCreate(**bird_data.model_dump()))

        if not new_bird:
            raise HTTPException(status_code=500, detail="Не удалось получить идентификатор курицы")

        new_bird_id = new_bird.get("id")

        return JSONResponse(status_code=200, content={"message": "Курицв успешно добавлена"})


    except SQLAlchemyError as e:
        logger.error(f"Ошибка при добавлении курицы: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка базы данных")
    except Exception as e:
        logger.error(f"Ошибка при добавлении курицы: {e}")
        raise HTTPException(status_code=500, detail="Неизвестная ошибка сервера")


@router.delete(
    path="/bakery/{bakery_id}/product/{product_id}/delete",
    summary="Удаление изделия по ID из хлебозавода по ID",
    responses={
        200: {"description": "Изделие успешно удалено"},
        404: {"description": "Изделие или хлебозавод не найдены"},
        500: {"description": "Ошибка сервера"}
    }
)
async def delete_product_by_bakery_and_product_id(
        bakery_id: int = Path(..., description="ID хлебозавода"),
        product_id: int = Path(..., description="ID изделия"),
        db: AsyncSession = Depends(db.get_db_with_commit)
) -> JSONResponse:
    try:
        bakery = await BakeryDao(db).find_one_or_none_by_id(bakery_id)
        if not bakery:
            raise HTTPException(status_code=404, detail=f"Хлебозавод с ID {bakery_id} не найден")

        product = await ProductDao(db).find_one_or_none_by_id(product_id)
        if not product or product.bakery_id != bakery_id:
            raise HTTPException(
                status_code=404,
                detail=f"Изделие с ID {product_id} не найдено для хлебозавода с ID {bakery_id}"
            )

        success = await ProductDao(db).delete_by_id(product_id)
        if success:
            return JSONResponse(
                status_code=200,
                content={"message": f"Изделие с ID {product_id} успешно удалено из хлебозавода с ID {bakery_id}"}
            )
        else:
            raise HTTPException(status_code=404, detail=f"Изделие с ID {product_id} не найдено")

    except SQLAlchemyError as e:
        logger.error(f"Ошибка при удалении изделия {product_id} из хлебозавода {bakery_id}: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка базы данных")
    except Exception as e:
        logger.error(f"Ошибка при удалении изделия {product_id} из хлебозавода {bakery_id}: {e}")
        raise HTTPException(status_code=500, detail="Неизвестная ошибка сервера")


@router.post("/update-egg-laying-rates")
async def update_egg_laying_rates_endpoint(session: AsyncSession = Depends(db.get_db_with_commit)):
    await BirdDao(session).update_egg_laying_rates()
    return {"status": "egg laying rates updated"}


@router.get("/birds/below_average")
async def birds_below_average(days: int = 30, session: AsyncSession = Depends(db.get_db)):
    bird_dao = BirdDao(session)
    result = await bird_dao.get_birds_below_average_egg_laying(days=days)
    return result

@router.get("/bird/max-eggs")
async def bird_with_max_eggs(session: AsyncSession = Depends(db.get_db)):
    dao = BirdDao(session)
    result = await dao.get_bird_with_max_eggs()
    return result