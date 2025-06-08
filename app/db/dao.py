from sqlalchemy.exc import SQLAlchemyError

from app.db.base import BaseDAO
from app.db.models import Bird, Cell, birds_in_cells

from loguru import logger

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import select, func, desc, insert

from app.schemas.bird import BirdCreate


class BirdDao(BaseDAO[Bird]):
    model = Bird

    async def update_egg_laying_rates(self, days: int = 30):
        today = datetime.now().date()
        start_date = today - timedelta(days=days)
        logger.info(f"Начинаем обновление яйценоскости за последние {days} дней с {start_date} по {today}")

        result = await self._session.execute(select(self.model))
        birds: List[Bird] = result.scalars().all()
        logger.info(f"Найдено птиц для обработки: {len(birds)}")

        for bird in birds:
            sum_eggs_query = (
                select(func.sum(Cell.number_of_eggs))
                .where(
                    Cell.cell_number == bird.cell_id,
                    Cell.date >= start_date
                )
            )
            sum_eggs_result = await self._session.execute(sum_eggs_query)
            sum_eggs = sum_eggs_result.scalar_one_or_none() or 0

            bird.egg_laying_rate = float(sum_eggs)
            logger.debug(f"Птица id={bird.id}, cell_number={bird.cell_id}, яйца за период: {sum_eggs}")

        await self._session.commit()
        logger.info("Обновление яйценоскости завершено и изменения сохранены в БД")

    async def get_birds_below_average_egg_laying(self, days: int = 30):
        today = datetime.now().date()
        start_date = today - timedelta(days=days)
        logger.info(f"Запрос птиц с яйценоскостью ниже средней за период с {start_date} по {today}")

        avg_query = select(func.avg(Bird.egg_laying_rate)).where(Bird.egg_laying_rate != None)
        avg_result = await self._session.execute(avg_query)
        avg_eggs = avg_result.scalar_one() or 0
        logger.info(f"Средняя яйценоскость по фабрике за период: {avg_eggs}")

        query = (
            select(Bird)
            .where(Bird.egg_laying_rate != None)
            .where(Bird.egg_laying_rate < avg_eggs)
        )

        result = await self._session.execute(query)
        birds = result.scalars().all()
        logger.info(f"Найдено птиц с яйценоскостью ниже средней: {len(birds)}")

        birds_below_avg = []
        for bird in birds:
            birds_below_avg.append({
                "bird_id": bird.id,
                "egg_laying_rate": float(bird.egg_laying_rate),
                "weight": float(bird.weight),
                "age": bird.age,
                "type_of_bird": bird.type_of_bird
            })
            logger.debug(f"Птица id={bird.id}, яйценоскость={bird.egg_laying_rate}")

        return {
            "average_egg_laying_rate": float(avg_eggs),
            "birds_below_average": birds_below_avg
        }

    async def get_bird_with_max_eggs(self):
        logger.info("Начинаем поиск птицы с максимальным количеством яиц у птицы")

        query = (
            select(Bird, Cell)
            .join(Cell, Bird.cell_id == Cell.cell_number)
            .order_by(desc(Cell.number_of_eggs))
            .limit(1)
        )

        result = await self._session.execute(query)
        row = result.first()

        if row is None:
            logger.info("Птицы для обработки не найдены")
            return None

        bird, cell = row
        logger.info(
            f"Птица с максимальным количеством яиц: id={bird.id}, яйца={cell.number_of_eggs}, номер клетки={cell.cell_number}")

        return {
            "bird_id": bird.id,
            "egg_laying_rate": float(bird.egg_laying_rate or 0),
            "total_eggs_in_cell": cell.number_of_eggs,
            "cell_number": cell.cell_number,
            "bird_weight": float(bird.weight),
            "bird_age": bird.age,
            "bird_type": bird.type_of_bird
        }


