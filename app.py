import streamlit as st
import asyncio
import datetime
from agents import Runner
from main import master_agent, config,study_plan_agent, quiz_agent, study_advice_agent
from model import StudentContext, StudyPlanOutput, QuizOutput, SummaryOutput

# --- App Configuration ---
st.set_page_config(
    page_title="📚 Student Exam Buddy",
    page_icon="🧠",
    layout="centered"
)

st.title("📚 Student Exam Buddy")
st.caption("Built by Mehdi Abbas Nathani!! • Powered by Gemini + OpenAI Agents SDK")

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

    # Prompt explicitly calls all three agent types
    prompt = (
        f"You are a master agent. The student named {name} is preparing for {subject} with an exam on {exam_date}. "
        f"Their weak topics are: {', '.join(weak_topics)}. Create a {total_days}-day study plan. Then generate a quiz on "
        f"at least one weak topic. Finally, give personalized advice based on their preparation status. you must call all three agents:{[study_plan_agent, quiz_agent, study_advice_agent]} "
    )

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
