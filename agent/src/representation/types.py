from pydantic import BaseModel, Field
from typing import List
class Step(BaseModel):
    title: str = Field(
        ..., description="Title of the step",
    )
    description: str = Field(
        ..., description="Description of the step",
    )

class Plan(BaseModel):
    thought: str = Field(
        ..., description="The agent's reasoning process and thought process",
    )
    background: str = Field(
        ..., description="Background context about the question",
    )
    title: str = Field(
        ..., description="Title of the plan",
    )
    steps: List[Step] = Field(
        default_factory=list,
        description="Steps to get more context",
    )