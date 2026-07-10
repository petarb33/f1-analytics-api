from typing import Literal
from pydantic import BaseModel


class GroupOptions(BaseModel):
    group: Literal["drivers", "teams"] = "drivers"


class DisplayOptions(BaseModel):
    display: Literal["absolute", "delta"] = "absolute"
