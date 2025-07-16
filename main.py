import os
from unittest import result
from dotenv import load_dotenv
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool
from agents.run import RunConfig
from model import ExamBuddyOutput, StudentContext, StudyPlanOutput, QuizOutput, SummaryOutput
from tools import study_plan, generate_quiz, summarize_notes, study_advice,get_student_context

import asyncio

# Load the environment variables from the .env file
load_dotenv()

# Assuming GEMINI_API_KEY is for Google's Gemini through OpenAI-compatible API
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
    model="gemini-2.0-flash", # Or 'gemini-1.5-pro' for more robust reasoning if needed
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True # Set to False if you want to see detailed traces
)

# Define tools after modifying them to include logging if desired
tools = [study_plan, generate_quiz, summarize_notes, study_advice]


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
    # Crucially updated instruction: Tell the agent to use the tool's output as the 'summary'.
    instructions=(
        "You provide personalized study advice based on the student's context including exam date and weak topics. "
        "You must use the `study_advice` tool to get the advice. "
        "Once you have the advice from the tool, provide it as the 'summary' field in the SummaryOutput."
    ),
    model=model,
    tools=[study_advice],
    output_type=SummaryOutput
)

master_agent = Agent[StudentContext](
    name="Master Student Exam Agent",
    instructions=(
        f"You are a master routing agent. Your job is to understand the student's input with their context named {StudentContext} "
        "and delegate the task to the correct sub-agent: use the Study Planner agent for planning, "
        "the Quiz agent for quizzes, and the Advice agent for personal guidance. "
        "Use the provided `name`, `subject`, `exam_date`, and `weak_topics` from the context."
    ),
    model=model,
    handoffs = [study_plan_agent, quiz_agent, study_advice_agent],
    tools=[get_student_context]  # Include the tool to fetch student context
)

async def main():
    # Initial Context
    student_context = StudentContext(
        name="Mehdi",
        subject="Physics",
        exam_date="2025-07-30", # Ensure this date is in the future for advice to be meaningful
        weak_topics=["Thermodynamics", "Laws of motion"]
    )

    result = await Runner.run(
        master_agent,
        "which topics should I focus on for my physics exam? and give me a quiz on thermodynamics",
        run_config=config,
        context=student_context
    )
    # ✅ Print Final Output
    print("\n\n📤 Final Output:")
    print(result.final_output)
    print("Last agent used:", result.last_agent.name) # Print agent name for clarity

if __name__ == "__main__":
    asyncio.run(main())