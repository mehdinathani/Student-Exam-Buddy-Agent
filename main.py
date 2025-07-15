import os
from unittest import result
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool
from agents.run import RunConfig
from model import ExamBuddyOutput, StudentContext, StudyPlanOutput, QuizOutput, SummaryOutput
from tools import study_plan, generate_quiz, summarize_notes, study_advice

import asyncio

# Load the environment variables from the .env file
load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

# Check if the API key is present; if not, raise an error
if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set. Please ensure it is defined in your .env file.")

#Reference: https://ai.google.dev/gemini-api/docs/openai
external_client = AsyncOpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

model = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

tools = [study_plan, generate_quiz, summarize_notes, study_advice]
# study_planner_agent = Agent(
#     name="Student Exam Buddy",
#     instructions="You assist students in preparing for exams. Use the user's context when answering.",
#     model=model,
#     tools=tools,
#     # output_type=ExamBuddyOutput
#   )

study_plan_agent = Agent[StudentContext](
    name="Study Planner Agent",
    instructions="You create a structured study plan for students based on their subject, exam date, and weak topics.",
    model=model,
    tools=[study_plan],
    output_type=StudyPlanOutput
)

quiz_agent = Agent[StudentContext](
    name="Quiz Generator Agent",
    instructions="You generate a short quiz for students based on a selected topic.",
    model=model,
    tools=[generate_quiz],
    output_type=QuizOutput
)

study_advice_agent = Agent[StudentContext](
    name="Study Advice Agent",
    instructions="You provide personalized study advice based on the student's context including exam date and weak topics.",
    model=model,
    tools=[study_advice],
    output_type=SummaryOutput  # if you’re using summary field to return advice
)

master_agent = Agent[StudentContext](
    name="Master Student Exam Agent",
    instructions=f"You are a master routing agent. Your job is to understand the student's input with their context named {StudentContext} and delegate the task to the correct sub-agent: use the Study Planner agent for planning, the Quiz agent for quizzes, and the Advice agent for personal guidance.Use the provided `name`, `subject`, `exam_date`, and `weak_topics` from the context.",
    model=model,
    handoffs = [study_plan_agent, quiz_agent, study_advice_agent],  
   
    )




async def main():
    # Initial Context
    student_context = StudentContext(
        name="Mehdi",
        subject="Physics",
        exam_date="2025-07-30",
        weak_topics=["Thermodynamics", "Laws of motion"]
    )


    result = await Runner.run(
        master_agent,
        "based on my context sgive me advice to be shine.",
        run_config=config,
        context=student_context
    )
    # ✅ Print Final Output
    print("📤 Final Output:")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())