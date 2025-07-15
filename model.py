from pydantic import BaseModel
from typing import List, Optional
from dataclasses import dataclass

class DayPlan(BaseModel):
    day: int
    topics: List[str]

class StudyPlanOutput(BaseModel):
    subject: str
    total_days: int
    plan: List[DayPlan]

class QuizQuestion(BaseModel):
    question: str
    answer: str

class QuizOutput(BaseModel):
    topic: str
    questions: List[QuizQuestion]

class SummaryOutput(BaseModel):
    summary: str

class ExamBuddyOutput(BaseModel):
    study_plan: Optional[StudyPlanOutput] = None
    quiz: Optional[QuizOutput] = None
    summary: Optional[SummaryOutput] = None



@dataclass
class StudentContext:
    name: str
    subject: str
    exam_date: str
    weak_topics: list[str]
