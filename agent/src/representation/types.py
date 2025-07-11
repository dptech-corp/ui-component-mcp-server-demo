from pydantic import BaseModel, Field
from typing import List
class Step(BaseModel):
    id: str = Field(
        ..., description="id of the step",
    )
    title: str = Field(
        ..., description="Title of the step",
    )

    sub_agent: str = Field(
        ..., description="candidate sub agent of the step, e.g. software_expert, microscopy_expert, representation_analyze_expert, theory_expert",
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