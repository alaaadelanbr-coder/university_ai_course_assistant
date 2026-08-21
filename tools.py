from datetime import date, datetime, timedelta
from typing import List
from langchain_core.tools import tool


# GPA values used for the 4.0 grading scale
GRADE_POINTS = {
    "A+": 4.0,
    "A": 4.0,
    "A-": 3.7,
    "B+": 3.3,
    "B": 3.0,
    "B-": 2.7,
    "C+": 2.3,
    "C": 2.0,
    "C-": 1.7,
    "D+": 1.3,
    "D": 1.0,
    "D-": 0.7,
    "F": 0.0,
}


@tool
def gpa_impact_simulator(
    current_gpa: float,
    completed_credits: float,
    course_credits: float,
    anticipated_grade: str,
) -> dict:
    """
    Calculate how a new course grade would affect the student's
    cumulative GPA.

    The tool takes the student's current GPA, completed credits,
    course credits, and expected grade, then returns the updated GPA
    along with a few useful details about the calculation.

    The GPA is calculated on a 4.0 scale. This is a deterministic
    calculation, so the result does not depend on the LLM or RAG.
    """

    # Make sure all numerical inputs have the expected type.
    if not isinstance(current_gpa, (int, float)):
        return {
            "status": "error",
            "message": "current_gpa must be a number."
        }

    if not isinstance(completed_credits, (int, float)):
        return {
            "status": "error",
            "message": "completed_credits must be a number."
        }

    if not isinstance(course_credits, (int, float)):
        return {
            "status": "error",
            "message": "course_credits must be a number."
        }

    if not isinstance(anticipated_grade, str):
        return {
            "status": "error",
            "message": "anticipated_grade must be a letter grade such as A, B+, or C-."
        }

    # Check that the GPA and credit values are reasonable.
    if current_gpa < 0 or current_gpa > 4:
        return {
            "status": "error",
            "message": "current_gpa must be between 0.0 and 4.0."
        }

    if completed_credits < 0:
        return {
            "status": "error",
            "message": "completed_credits cannot be negative."
        }

    if course_credits <= 0:
        return {
            "status": "error",
            "message": "course_credits must be greater than 0."
        }

    # Normalize the grade before checking it against our grading scale.
    grade = anticipated_grade.strip().upper()

    if grade not in GRADE_POINTS:
        return {
            "status": "error",
            "message": (
                f"Invalid grade '{anticipated_grade}'. "
                f"Supported grades are: {', '.join(GRADE_POINTS.keys())}."
            )
        }

    grade_points = GRADE_POINTS[grade]

    # Calculate the updated GPA from the current and new course
    # quality points.
    current_quality_points = current_gpa * completed_credits
    new_course_quality_points = grade_points * course_credits

    total_credits = completed_credits + course_credits

    updated_gpa = (
        current_quality_points + new_course_quality_points
    ) / total_credits

    # Keep the result within the 4.0 GPA scale.
    updated_gpa = min(max(updated_gpa, 0.0), 4.0)

    return {
        "status": "success",
        "current_gpa": round(current_gpa, 2),
        "completed_credits": round(completed_credits, 2),
        "course_credits": round(course_credits, 2),
        "anticipated_grade": grade,
        "grade_points": grade_points,
        "updated_gpa": round(updated_gpa, 2),
        "gpa_change": round(updated_gpa - current_gpa, 2),
        "total_credits_after_course": round(total_credits, 2),
    }


@tool
def generate_study_schedule(
    topics: List[str],
    exam_date: str,
    available_hours_per_day: float,
) -> dict:
    """
    Create a day-by-day study schedule based on the student's
    topics, exam date, and available study time.

    The topics are expected to come from the syllabus or RAG context.
    This tool only handles the scheduling itself; it does not search
    the syllabus or retrieve course information.
    """

    # Clean up the topic list and make sure every topic is valid.
    if not isinstance(topics, list):
        return {
            "status": "error",
            "message": "topics must be a list of topic names."
        }

    cleaned_topics = []

    for topic in topics:
        if not isinstance(topic, str):
            return {
                "status": "error",
                "message": "Every topic must be a string."
            }

        cleaned_topic = topic.strip()

        if cleaned_topic:
            cleaned_topics.append(cleaned_topic)

    if not cleaned_topics:
        return {
            "status": "error",
            "message": "At least one valid study topic is required."
        }

    # Remove duplicate topics while keeping their original order.
    cleaned_topics = list(dict.fromkeys(cleaned_topics))

    # Check that the available study time is valid.
    if not isinstance(available_hours_per_day, (int, float)):
        return {
            "status": "error",
            "message": "available_hours_per_day must be a number."
        }

    if available_hours_per_day <= 0:
        return {
            "status": "error",
            "message": "available_hours_per_day must be greater than 0."
        }

    if available_hours_per_day > 24:
        return {
            "status": "error",
            "message": "available_hours_per_day cannot exceed 24 hours."
        }

    # Convert the exam date from text to a date object.
    try:
        exam = datetime.strptime(exam_date, "%Y-%m-%d").date()
    except ValueError:
        return {
            "status": "error",
            "message": "exam_date must use YYYY-MM-DD format."
        }

    today = date.today()
    days_remaining = (exam - today).days

    # We need at least one full day before the exam to build a schedule.
    if days_remaining < 0:
        return {
            "status": "error",
            "message": "The exam date has already passed.",
            "exam_date": exam_date,
            "today": today.isoformat(),
        }

    if days_remaining == 0:
        return {
            "status": "error",
            "message": "The exam is today. No future study days are available.",
            "exam_date": exam_date,
        }

    study_days = days_remaining

    # Calculate how many study hours are available in total.
    total_study_hours = study_days * available_hours_per_day

    # Divide the total study time evenly across the topics.
    number_of_topics = len(cleaned_topics)
    base_hours_per_topic = total_study_hours / number_of_topics

    topic_hours = {}

    for topic in cleaned_topics:
        topic_hours[topic] = round(base_hours_per_topic, 2)

    # Fix any small rounding difference so the topic hours
    # still add up to the total available study time.
    rounded_total = sum(topic_hours.values())
    rounding_difference = round(total_study_hours - rounded_total, 2)

    if rounding_difference != 0:
        last_topic = cleaned_topics[-1]
        topic_hours[last_topic] = round(
            topic_hours[last_topic] + rounding_difference,
            2
        )

    # Build the schedule one day at a time.
    schedule = []
    topic_index = 0

    for day_number in range(1, study_days + 1):

        study_date = today + timedelta(days=day_number)

        # Spread the available time across the topics for this day.
        daily_topic_hours = {}

        for _ in range(number_of_topics):
            topic = cleaned_topics[topic_index % number_of_topics]

            daily_topic_hours[topic] = round(
                daily_topic_hours.get(topic, 0)
                + (available_hours_per_day / number_of_topics),
                2
            )

            topic_index += 1

        schedule.append(
            {
                "day": day_number,
                "date": study_date.isoformat(),
                "hours_available": round(
                    available_hours_per_day,
                    2
                ),
                "topics": daily_topic_hours,
            }
        )

    return {
        "status": "success",
        "exam_date": exam.isoformat(),
        "today": today.isoformat(),
        "days_remaining": days_remaining,
        "number_of_topics": number_of_topics,
        "total_study_hours": round(total_study_hours, 2),
        "available_hours_per_day": round(
            available_hours_per_day,
            2
        ),
        "topic_hours": topic_hours,
        "schedule": schedule,
    }


# These are the tools that will be passed to the Agent.
TOOLS = [
    gpa_impact_simulator,
    generate_study_schedule,
]
