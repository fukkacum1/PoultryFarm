from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, validator, field_validator

class BirdMaxEggsResponse(BaseModel):
    bird_id: int
    egg_laying_rate: float
    total_eggs_in_cell: int
    cell_id: int
    cell_number: int
    bird_weight: float
    bird_age: int
    bird_type: str


class BirdCreate(BaseModel):
    cell_id: int = Field(..., description="ID клетки, в которой находится птица")
    weight: Decimal = Field(..., description="Вес птицы (в кг)")
    age: int = Field(..., description="Возраст птицы (в месяцах)")
    type_of_bird: str = Field(..., description="Тип птицы (порода)")
    egg_laying_rate: Optional[Decimal] = Field(None, description="Яйценоскость (яиц в день)")
