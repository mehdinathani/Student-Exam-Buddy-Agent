from datetime import datetime
from agents import function_tool, RunContextWrapper
from model import StudentContext

# @function_tool
# def study_plan(subject: str, days: int) -> str:
#     """
#     Generates a day-wise study plan for a given subject and number of days.
#     """
#     return f"Create a {days}-day study plan for the subject of {subject}. List topics for each day in detail."

# generate_quiz(topic: str, num_questions: int)

@function_tool
def generate_quiz(topic: str, num_questions: int) -> str:
    """
    Generates a quiz with the given topic and number of questions.
    """
    return f"Create a quiz on the topic of {topic} with {num_questions} questions."

# summarize_notes(notes: str) -> str
@function_tool
def summarize_notes(notes: str) -> str:
    """
    Summarizes the given notes.
    """
    return f"Summarize the following notes: {notes}"


@function_tool
async def study_plan(wrapper: RunContextWrapper[StudentContext]) -> str:
    ctx = wrapper.context
    return (
        f"Create a 5-day study plan for {ctx.name} who is preparing for {ctx.subject}."
        f"The exam is on {ctx.exam_date}. Prioritize weak topics: {', '.join(ctx.weak_topics)} with detailed topics."
    )

@function_tool
async def study_advice(wrapper: RunContextWrapper[StudentContext],request: str = "Give advice") -> str:
    
    ctx = wrapper.context
    name = ctx.name
    subject = ctx.subject
    weak_topics = ", ".join(ctx.weak_topics)
    print(f"Create a study advice for {name} on {subject} with weak topics: {weak_topics}")
    
    # Days left until exam
    try:
        exam_date = datetime.strptime(ctx.exam_date, "%Y-%m-%d")
        today = datetime.today()
        days_left = (exam_date - today).days
    except:
        days_left = None

    # Build advice string
    advice = f"Hi {name}, you're preparing for {subject}."
    if days_left is not None:
        advice += f" You have only {days_left} days left until your exam."
        if days_left < 3:
            advice += " That's a short time — focus on revision and don't start new topics."
        elif days_left < 7:
            advice += " Use your time wisely; make sure to review weak areas and stay consistent."
        else:
            advice += " Great, you have time. Plan well and take care of yourself too."

    advice += f" Your weak topics are: {weak_topics}. Prioritize them every day."

    advice += " Stay focused, avoid burnout, and trust your preparation."

    return advice

def log_tool_call(tool_func):
    async def wrapper(*args, **kwargs):
        print(f"\n🛠️ Tool Called: {tool_func.__name__}")
        print(f"   Args: {args}")
        print(f"   Kwargs: {kwargs}")
        return await tool_func(*args, **kwargs)
    return wrapper

@function_tool
def get_student_context(wrapper: RunContextWrapper[StudentContext]) -> StudentContext:
    """
    Extracts the StudentContext from the RunContextWrapper.
    """
    return wrapper.context