import streamlit as st
import asyncio
from agents import Runner
from main import master_agent, config
from model import StudentContext
import datetime

st.set_page_config(page_title="📚 Student Exam Buddy", page_icon="🧠", layout="centered")
st.title("📚 Student Exam Buddy")
st.caption("Built by Mehdi Abbas Nathani • Powered by Gemini + OpenAI Agents SDK")

# --- Sidebar Context Form ---
st.sidebar.header("📝 Enter Exam Context")
name = st.sidebar.text_input("Your Name", "Mehdi")
subject = st.sidebar.selectbox("Subject", ["Physics", "Mathematics", "Biology", "Chemistry", "Computer Science"])
exam_date = st.sidebar.date_input("Exam Date", datetime.date(2025, 7, 30))
weak_topics_input = st.sidebar.text_area("Weak Topics (comma-separated)", "Thermodynamics, Laws of motion")
generate = st.sidebar.button("🔍 Generate Plan")

# --- Action Handler ---
if generate:
    weak_topics = [topic.strip() for topic in weak_topics_input.split(",") if topic.strip()]
    student_context = StudentContext(
        name=name,
        subject=subject,
        exam_date=str(exam_date),
        weak_topics=weak_topics
    )

    with st.spinner("🤖 Thinking... Calling agents..."):
        result = asyncio.run(Runner.run(
            starting_agent=master_agent,
            input=f"Create a study plan, quiz, and give me personalized advice based on {student_context}.",
            context=student_context,
            run_config=config
        ))

    output = result.final_output
    st.success("✅ Results ready!")

    # --- Structured Output Display ---
    if hasattr(output, 'plan') and output.plan:
        st.subheader("📅 Study Plan")
        for day in output.plan:
            with st.expander(f"Day {day.day}"):
                for topic in day.topics:
                    st.markdown(f"- ✅ {topic}")

    if hasattr(output, 'questions') and output.questions:
        st.subheader("🧪 Quiz")
        for idx, q in enumerate(output.questions):
            st.markdown(f"**Q{idx + 1}:** {q.question}")
            st.markdown(f"➡️ **Answer:** {q.answer}")
            st.markdown("---")

    if hasattr(output, 'summary') and output.summary:
        st.subheader("💡 Study Advice")
        st.info(output.summary)

    st.caption(f"🔁 Last agent used: `{result.last_agent.name}`")

else:
    st.info("👈 Please fill the form and click 'Generate Plan' to begin.")
