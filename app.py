import streamlit as st
import asyncio
import datetime
from agents import Runner
from main import master_agent, config
from model import StudentContext

# --- App Configuration ---
st.set_page_config(
    page_title="📚 Student Exam Buddy",
    page_icon="🧠",
    layout="centered"
)

st.title("📚 Student Exam Buddy")
st.caption("Built by Mehdi Abbas Nathani • Powered by Gemini + OpenAI Agents SDK")

# --- Sidebar Input Form ---
st.sidebar.header("📝 Enter Exam Context")

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

generate = st.sidebar.button("🔍 Generate Plan")

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

    # LLM prompt to master agent
    prompt = f"Create a {total_days}-day study plan, quiz, and give me personalized advice."

    with st.spinner("🤖 Thinking... Agents at work..."):
        result = asyncio.run(Runner.run(
            starting_agent=master_agent,
            input=prompt,
            context=student_context,
            run_config=config
        ))

    output = result.final_output
    st.success("✅ Results ready!")

    # --- Display Study Plan ---
    if hasattr(output, 'plan') and output.plan:
        st.subheader("📅 Study Plan")
        for day in output.plan:
            with st.expander(f"Day {day.day}"):
                for topic in day.topics:
                    st.markdown(f"✅ {topic}")

    # --- Display Quiz ---
    if hasattr(output, 'questions') and output.questions:
        st.subheader("🧪 Quiz")
        for idx, q in enumerate(output.questions):
            st.markdown(f"**Q{idx + 1}:** {q.question}")
            st.markdown(f"➡️ **Answer:** {q.answer}")
            st.markdown("---")

    # --- Display Study Advice ---
    if hasattr(output, 'summary') and output.summary:
        st.subheader("💡 Study Advice")
        st.info(output.summary)

    # --- Agent Routing Info ---
    st.caption(f"🔁 Routed via: `{result.last_agent.name}`")

else:
    st.info("👈 Fill in the exam details and press 'Generate Plan' to begin.")
