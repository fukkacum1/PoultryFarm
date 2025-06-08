from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Date, Numeric, ForeignKey, Table, Column
from datetime import date
from typing import List
from app.db.database import Base

class Cell(Base):
    __tablename__ = "cells"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)



class Cell(Base):
    __tablename__ = "cells"

    id = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    number_of_eggs: Mapped[int] = mapped_column(Integer, nullable=True)

    birds: Mapped[List["Bird"]] = relationship(
        "Bird",
        secondary=birds_in_cells,
        back_populates="cells",
        uselist=True
    )

    worker_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("workers.id"), nullable=True)
    worker: Mapped["Worker"] = relationship("Worker", back_populates="cells")


    def repr(self):
        return f"<Cell(id={self.id}, bird_id={self.bird_id}, worker_id={self.worker_id}, date={self.date}, number_of_eggs={self.number_of_eggs})>"


class Bird(Base):
    __tablename__ = "birds"

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    cell_id: Mapped[int] = mapped_column(Integer, ForeignKey("cells.id"), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(10, 3), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    type_of_bird: Mapped[str] = mapped_column(String, nullable=False)
    egg_laying_rate: Mapped[float | None] = mapped_column(Numeric(10, 3), nullable=True)

    cells: Mapped[List["Cell"]] = relationship(
        "Cell",
        secondary=birds_in_cells,
        back_populates="birds",
        uselist=True
    )
    def __repr__(self):
        return f"<Bird(id={self.id}, cell_id={self.cell_id}, egg_laying_rate={self.egg_laying_rate})>"


class Worker(Base):
    __tablename__ = "workers"

    id = mapped_column(Integer, primary_key=True)
    fio: Mapped[str] = mapped_column(String, nullable=False)
    salary: Mapped[int] = mapped_column(Integer, nullable=False)

    cells: Mapped[List["Cell"]] = relationship("Cell", back_populates="worker")

    def __repr__(self):
        return f"<Worker(id={self.id}, fio={self.fio}, salary={self.salary})>"
