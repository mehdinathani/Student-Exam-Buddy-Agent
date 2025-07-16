import streamlit as st
import asyncio
import datetime
from agents import Runner
from main import master_agent, config, study_plan_agent, quiz_agent, study_advice_agent
from model import StudentContext

# --- App Configuration ---
st.set_page_config(
    page_title="\ud83d\udcda Student Exam Buddy",
    page_icon="\ud83e\udde0",
    layout="centered"
)

st.title("\ud83d\udcda Student Exam Buddy")
st.caption("Built by Mehdi Abbas Nathani!! • Powered by Gemini + OpenAI Agents SDK")

# --- Sidebar Input Form ---
st.sidebar.header("\ud83d\udcdd Enter Exam Context")

name = st.sidebar.text_input("Your Name", "Mehdi")

subject = st.sidebar.selectbox(
    "Subject",
    ["Physics", "Mathematics", "Biology", "Chemistry", "Computer Science"]
)

exam_date = st.sidebar.date_input(
    "Exam Date",
    value=datetime.date(2025, 7, 30),
    min_value=datetime.date.today()
)

weak_topics = st.sidebar.multiselect(
    "Weak Topics (select or type new and press Enter)",
    options=["Thermodynamics", "Laws of motion", "Electricity", "Magnetism", "Quantum Mechanics"],
    default=["Thermodynamics", "Laws of motion"]
)

generate = st.sidebar.button("\ud83d\udd0d Generate Plan")

# --- On Generate Click ---
if generate:
    today = datetime.date.today()
    total_days = max((exam_date - today).days, 1)

    student_context = StudentContext(
        name=name,
        subject=subject,
        exam_date=str(exam_date),
        weak_topics=weak_topics
    )

    # Prompts for each sub-agent
    study_prompt = f"Create a {total_days}-day study plan that prioritizes the weak topics."
    quiz_prompt = f"Generate a short quiz on the topic '{weak_topics[0]}' for exam preparation."
    advice_prompt = "Give me personalized study advice based on my context."

    with st.spinner("\ud83e\udde0 Thinking... Agents at work..."):
        study_result = asyncio.run(Runner.run(
            starting_agent=study_plan_agent,
            input=study_prompt,
            context=student_context,
            run_config=config
        ))

        quiz_result = asyncio.run(Runner.run(
            starting_agent=quiz_agent,
            input=quiz_prompt,
            context=student_context,
            run_config=config
        ))

        advice_result = asyncio.run(Runner.run(
            starting_agent=study_advice_agent,
            input=advice_prompt,
            context=student_context,
            run_config=config
        ))

    st.success("\u2705 Results ready!")

    # --- Display Study Plan ---
    if hasattr(study_result.final_output, 'plan') and study_result.final_output.plan:
        st.subheader("\ud83d\udcc5 Study Plan")
        for day in study_result.final_output.plan:
            with st.expander(f"Day {day.day}"):
                for topic in day.topics:
                    st.markdown(f"\u2705 {topic}")

    # --- Display Quiz ---
    if hasattr(quiz_result.final_output, 'questions') and quiz_result.final_output.questions:
        st.subheader("\ud83e\uddea Quiz")
        for idx, q in enumerate(quiz_result.final_output.questions):
            st.markdown(f"**Q{idx + 1}:** {q.question}")
            st.markdown(f"\u27a1\ufe0f **Answer:** {q.answer}")
            st.markdown("---")

    # --- Display Study Advice ---
    if hasattr(advice_result.final_output, 'summary') and advice_result.final_output.summary:
        st.subheader("\ud83d\udca1 Study Advice")
        st.info(advice_result.final_output.summary)

    # --- Agent Routing Info ---
    st.caption(f"\ud83d\udd01 Routed via: study_plan_agent, quiz_agent, study_advice_agent")

else:
    st.info("\ud83d\udc48 Fill in the exam details and press 'Generate Plan' to begin.")
