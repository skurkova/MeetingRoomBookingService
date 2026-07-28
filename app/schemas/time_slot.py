from pydantic import BaseModel, ConfigDict
from datetime import time


class TimeSlotResponse(BaseModel):
    """Схема временного интервала"""

    id: int
    start_time: time
    end_time: time

    model_config = ConfigDict(from_attributes=True)
