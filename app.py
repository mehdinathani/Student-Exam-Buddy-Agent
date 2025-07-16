import streamlit as st
import asyncio
from agents import Runner
from main import master_agent  # <-- you must create this import
from model import StudentContext
from agents.run import RunConfig
from dotenv import load_dotenv
import os

# Load .env
load_dotenv()

# Setup your context
student_context = StudentContext(
    name="Mehdi",
    subject="Physics",
    exam_date="2025-07-30",
    weak_topics=["Thermodynamics", "Laws of motion"]
)

# Configuration
config = RunConfig(
    model=master_agent.model,
    
    tracing_disabled=True
)

st.title("📚 Student Exam Buddy")

user_input = st.text_area("Ask your buddy:", "Give me advice to shine in my exam")

if st.button("Ask Agent"):
    with st.spinner("Thinking..."):
        result = asyncio.run(Runner.run(
            starting_agent=master_agent,
            input=user_input,
            context=student_context,
            run_config=config
        ))
        st.success("Done!")

        # Show results
        st.write("### 🤖 Agent Output:")
        st.json(result.final_output)

        st.caption(f"Last agent used: {result.last_agent.name}")
