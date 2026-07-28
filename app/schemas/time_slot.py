from datetime import time

from pydantic import BaseModel, ConfigDict


class TimeSlotResponse(BaseModel):
    """Схема временного интервала"""

    id: int
    start_time: time
    end_time: time

    model_config = ConfigDict(from_attributes=True)
