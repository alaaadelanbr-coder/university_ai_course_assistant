from datetime import date, datetime, timedelta
from typing import List

from langchain_core.tools import tool


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
    Calculate the updated cumulative GPA after adding one course.
    """

    if not 0 <= current_gpa <= 4:
        return {
            "status": "error",
            "message": "GPA must be between 0 and 4.",
        }

    if completed_credits < 0:
        return {
            "status": "error",
            "message": "Completed credits cannot be negative.",
        }

    if course_credits <= 0:
        return {
            "status": "error",
            "message": "Course credits must be greater than 0.",
        }

    grade = anticipated_grade.strip().upper()

    if grade not in GRADE_POINTS:
        return {
            "status": "error",
            "message": (
                f"Invalid grade '{anticipated_grade}'. "
                f"Supported grades: {', '.join(GRADE_POINTS)}."
            ),
        }

    grade_points = GRADE_POINTS[grade]

    old_quality_points = current_gpa * completed_credits
    new_quality_points = grade_points * course_credits
    total_credits = completed_credits + course_credits

    updated_gpa = (
        old_quality_points + new_quality_points
    ) / total_credits

    updated_gpa = round(updated_gpa, 2)

    return {
        "status": "success",
        "current_gpa": round(current_gpa, 2),
        "grade": grade,
        "grade_points": grade_points,
        "updated_gpa": updated_gpa,
        "gpa_change": round(updated_gpa - current_gpa, 2),
        "total_credits": round(total_credits, 2),
    }


def _clean_topics(topics: List[str]) -> List[str]:
    topics = [
        topic.strip()
        for topic in topics
        if isinstance(topic, str) and topic.strip()
    ]

    return list(dict.fromkeys(topics))


def _get_dates(exam_date: str):
    try:
        exam = datetime.strptime(
            exam_date,
            "%Y-%m-%d",
        ).date()
    except ValueError:
        return None, "exam_date must use YYYY-MM-DD format."

    today = date.today()
    days_until_exam = (exam - today).days

    if days_until_exam <= 0:
        return None, (
            "The exam must be at least one day in the future."
        )

    study_days = days_until_exam - 1

    if study_days <= 0:
        return None, (
            "There is no full study day available before the exam."
        )

    return (today, exam, study_days), None


def _choose_day_types(study_days: int):
    if study_days >= 21:
        review_days = 3
        rest_days = 3
    elif study_days >= 14:
        review_days = 2
        rest_days = 2
    elif study_days >= 8:
        review_days = 2
        rest_days = 1
    elif study_days >= 5:
        review_days = 1
        rest_days = 0
    else:
        review_days = 0
        rest_days = 0

    if review_days + rest_days >= study_days:
        review_days = 0
        rest_days = 0

    main_days = study_days - review_days - rest_days

    return main_days, review_days, rest_days


@tool
def generate_study_schedule(
    topics: List[str],
    exam_date: str,
    available_hours_per_day: float,
    priority_topics: List[str] = None,
) -> dict:
    """
    Generate a study schedule with topic blocks, review days,
    and rest days when enough preparation time is available.
    """

    if not isinstance(topics, list):
        return {
            "status": "error",
            "message": "topics must be a list.",
        }

    topics = _clean_topics(topics)

    if not topics:
        return {
            "status": "error",
            "message": "At least one valid topic is required.",
        }

    if not isinstance(available_hours_per_day, (int, float)):
        return {
            "status": "error",
            "message": "available_hours_per_day must be a number.",
        }

    if not 0 < available_hours_per_day <= 24:
        return {
            "status": "error",
            "message": "Study hours must be between 0 and 24.",
        }

    dates, error = _get_dates(exam_date)

    if error:
        return {
            "status": "error",
            "message": error,
        }

    today, exam, study_days = dates

    priority_topics = _clean_topics(
        priority_topics or []
    )

    priority_topics = [
        topic
        for topic in priority_topics
        if topic in topics
    ]

    ordered_topics = priority_topics + [
        topic
        for topic in topics
        if topic not in priority_topics
    ]

    main_days, review_days, rest_days = _choose_day_types(
        study_days
    )

    topic_count = len(ordered_topics)

    # Give priority topics more days.
    weights = [2 if topic in priority_topics else 1
               for topic in ordered_topics]

    total_weight = sum(weights)

    block_days = []

    for weight in weights:
        block_days.append(
            max(1, round(main_days * weight / total_weight))
        )

    # Keep total main-study days exact.
    while sum(block_days) > main_days:
        largest = max(
            range(topic_count),
            key=lambda i: block_days[i],
        )

        if block_days[largest] > 1:
            block_days[largest] -= 1
        else:
            break

    while sum(block_days) < main_days:
        smallest = min(
            range(topic_count),
            key=lambda i: block_days[i],
        )
        block_days[smallest] += 1

    schedule = []
    day_number = 1

    # Main topic blocks.
    for topic, days_for_topic in zip(
        ordered_topics,
        block_days,
    ):
        for _ in range(days_for_topic):
            current_date = today + timedelta(
                days=day_number
            )

            schedule.append(
                {
                    "day": day_number,
                    "date": current_date.isoformat(),
                    "phase": "Main Study",
                    "focus": topic,
                    "hours": round(
                        float(available_hours_per_day),
                        2,
                    ),
                }
            )

            day_number += 1

    # Add rest days.
    if rest_days:
        spacing = max(
            1,
            main_days // (rest_days + 1),
        )

        rest_positions = {
            spacing * (i + 1)
            for i in range(rest_days)
        }

        for day in schedule:
            if day["day"] in rest_positions:
                day["phase"] = "Rest"
                day["focus"] = "Rest day"
                day["hours"] = 0.0

    # Final review days.
    for _ in range(review_days):
        current_date = today + timedelta(
            days=day_number
        )

        focus = ordered_topics[
            (day_number - 1) % topic_count
        ]

        schedule.append(
            {
                "day": day_number,
                "date": current_date.isoformat(),
                "phase": "Review",
                "focus": focus,
                "hours": round(
                    float(available_hours_per_day),
                    2,
                ),
            }
        )

        day_number += 1

    return {
        "status": "success",
        "exam_date": exam.isoformat(),
        "today": today.isoformat(),
        "study_days_before_exam": study_days,
        "main_study_days": main_days,
        "rest_days": rest_days,
        "review_days": review_days,
        "schedule": schedule,
    }


@tool
def edit_study_schedule(
    schedule: List[dict],
    action: str,
    date_value: str,
    topic: str = "",
    new_topic: str = "",
    hours: float = 0,
    target_date: str = "",
) -> dict:
    """
    Edit one part of an existing study schedule.

    Supported actions:
    rest
    set_hours
    replace_topic
    move_topic
    """

    updated = [
        dict(day)
        for day in schedule
    ]

    target = next(
        (
            day
            for day in updated
            if day.get("date") == date_value
        ),
        None,
    )

    if target is None:
        return {
            "status": "error",
            "message": f"No schedule entry for {date_value}.",
        }

    if action == "rest":
        target["phase"] = "Rest"
        target["focus"] = "Rest day"
        target["hours"] = 0.0

    elif action == "set_hours":
        if not 0 < hours <= 24:
            return {
                "status": "error",
                "message": "Hours must be between 0 and 24.",
            }

        target["hours"] = round(hours, 2)

    elif action == "replace_topic":
        if not new_topic.strip():
            return {
                "status": "error",
                "message": "A new topic is required.",
            }

        target["focus"] = new_topic.strip()

    elif action == "move_topic":
        destination = next(
            (
                day
                for day in updated
                if day.get("date") == target_date
            ),
            None,
        )

        if destination is None:
            return {
                "status": "error",
                "message": (
                    f"No schedule entry for {target_date}."
                ),
            }

        target["focus"] = ""
        destination["focus"] = topic
        destination["hours"] = round(hours, 2)

    else:
        return {
            "status": "error",
            "message": (
                "Supported actions: rest, set_hours, "
                "replace_topic, move_topic."
            ),
        }

    return {
        "status": "success",
        "message": "Schedule updated successfully.",
        "schedule": updated,
    }


TOOLS = [
    gpa_impact_simulator,
    generate_study_schedule,
    edit_study_schedule,
]