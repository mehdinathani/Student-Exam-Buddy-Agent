import asyncio
from dataclasses import dataclass
from dotenv import load_dotenv
from agents import AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, Runner,RunContextWrapper,Agent,RunConfig
import os


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

# Define a simple context using a dataclass
@dataclass
class UserInfo:  
    name: str
    uid: int

# A tool function that accesses local context via the wrapper
@function_tool
async def fetch_user_age(wrapper: RunContextWrapper[UserInfo]) -> str:  
    return f"User {wrapper.context.name} is 47 years old"

async def main():
    # Create your context object
    user_info = UserInfo(name="John", uid=123)  

    # Define an agent that will use the tool above
    agent = Agent[UserInfo](  
        name="Assistant",
        tools=[fetch_user_age],
        model=model,
    )

    # Run the agent, passing in the local context
    result = await Runner.run(
        starting_agent=agent,
        input="What is the age of the user?",
        context=user_info,
        run_config=config,
    )

    print(result.final_output)  # Expected output: The user John is 47 years old.

if __name__ == "__main__":
    asyncio.run(main())