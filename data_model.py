from typing import Union
from pydantic import BaseModel


class Input(BaseModel):
    job_description: str
    resume: str
    request_id: str


class GetInsightsInput(BaseModel):
    applicant_id: str