import operator
from typing import Annotated, Literal, Optional, TypedDict

from pydantic import BaseModel, Field


class Claim(BaseModel):
    order_id: Optional[str] = Field(description="Order id such as HS2291, or null if the message has none")
    pincode: Optional[str] = Field(description="6-digit pickup pincode, or null if the message has none")
    issue_type: Literal["wrong_size", "defect", "changed_mind", "other"] = Field(description="What the customer says is wrong")
    wants: Literal["exchange", "refund", "unclear"] = Field(description="What the customer asks for")


class Tone(BaseModel):
    tone: Literal["calm", "upset", "angry"] = Field(description="How the customer sounds in the message")


class DeskState(TypedDict):
    message: str

    claim: dict
    tone: str

    messages: Annotated[list, operator.add]
    trips: int

    exit: Literal["approve", "decline", "escalate"]
    reason: str
    action: str
    reply: str
    status: str
