from pydantic import BaseModel
from typing import List, Union, Tuple
from enum import Enum


class Role(str, Enum):
    HIDER = "hider"
    SEEKER = "seeker"


class Status(str, Enum):
    SUCCESS = "success"
    FAIL = "fail"


class JoinGameRequest(BaseModel):
    """The message from the client requesting the role."""

    role: Role


class SuccessFailMessage(BaseModel):
    """Response sent to the client whether the request succeeded or failed"""

    status: Status


class GridUpdateMessage(BaseModel):
    """Status update sent to the client after a game step"""

    grid: List[List[int]]
    seeker_can_see: bool


class UpdateMoveRequest(BaseModel):
    move: Union[Tuple[int, int], Tuple[()]]


class GameOverMessage(BaseModel):
    game_steps: int
