import streamlit as st
import asyncio
import datetime
from agents import Runner
from main import master_agent, config, study_plan_agent, quiz_agent, study_advice_agent
from model import StudentContext

# --- App Configuration ---
st.set_page_config(
    page_title="Student Exam Buddy",   # ✅ plain ASCII
    page_icon=":books:",               # ✅ Streamlit emoji code
    layout="centered"
)


st.title(":books: Student Exam Buddy")
st.caption("Built by Mehdi Abbas Nathani • Powered by Gemini + OpenAI Agents SDK")


# --- Sidebar Input Form ---
st.sidebar.header("Enter Exam Context")

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

generate = st.sidebar.button("Generate Plan")

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
    study_prompt = f"Create a {total_days}-day study plan that prioritizes the weak topics from {student_context}."
    quiz_prompt = f"Generate a short quiz on the topic '{weak_topics[0]}' for exam preparation from {student_context}."
    advice_prompt = f"Give me personalized study advice based on my context from {student_context}."

    with st.spinner("Thinking... Agents at work..."):
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

    st.success("Results ready!")

    # --- Display Study Plan ---
    if hasattr(study_result.final_output, 'plan') and study_result.final_output.plan:
        st.subheader("Study Plan")
        for day in study_result.final_output.plan:
            with st.expander(f"Day {day.day}"):
                for topic in day.topics:
                    st.markdown(f"{topic}")

    # --- Display Quiz ---
    if hasattr(quiz_result.final_output, 'questions') and quiz_result.final_output.questions:
        st.subheader("Quiz")
        for idx, q in enumerate(quiz_result.final_output.questions):
            st.markdown(f"**Q{idx + 1}:** {q.question}")
            st.markdown(f"**Answer:** {q.answer}")
            st.markdown("---")

    # --- Display Study Advice ---
    if hasattr(advice_result.final_output, 'summary') and advice_result.final_output.summary:
        st.subheader("Study Advice")
        st.info(advice_result.final_output.summary)

    # --- Agent Routing Info ---
    st.caption(f"Routed via: study_plan_agent, quiz_agent, study_advice_agent")

else:
    st.info("Fill in the exam details and press 'Generate Plan' to begin.")
