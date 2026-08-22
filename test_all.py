from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def print_result(name: str, passed: bool, details: str = ""):
    status = "PASS" if passed else "FAIL"

    print("\n" + "=" * 70)
    print(f"{status}: {name}")
    print("=" * 70)

    if details:
        print(details)


def test_health():
    response = client.get("/")

    passed = (
        response.status_code == 200
        and response.json().get("message")
        == "Syllabus & Exam Assistant API is running."
    )

    print_result(
        "FastAPI Health Check",
        passed,
        f"Status: {response.status_code}\n"
        f"Response: {response.json()}",
    )

    return passed


def test_rag():
    response = client.post(
        "/chat",
        json={
            "question": "What is the final exam worth?",
            "session_id": "rag-test",
        },
    )

    body = response.json()
    answer = body.get("answer", "")

    passed = (
        response.status_code == 200
        and isinstance(answer, str)
        and len(answer.strip()) > 0
    )

    print_result(
        "RAG + Agent + FastAPI",
        passed,
        f"Status: {response.status_code}\n"
        f"Answer:\n{answer}",
    )

    return passed


def test_grounding():
    response = client.post(
        "/chat",
        json={
            "question": (
                "What is the instructor's favorite programming language?"
            ),
            "session_id": "grounding-test",
        },
    )

    body = response.json()
    answer = body.get("answer", "").lower()

    fallback_terms = [
        "not found",
        "couldn't find",
        "could not find",
        "consult",
        "teaching assistant",
        "instructor",
    ]

    passed = (
        response.status_code == 200
        and any(term in answer for term in fallback_terms)
    )

    print_result(
        "Grounding / Missing Information Guardrail",
        passed,
        f"Status: {response.status_code}\n"
        f"Answer:\n{body.get('answer', '')}",
    )

    return passed


def test_gpa():
    response = client.post(
        "/chat",
        json={
            "question": (
                "My current GPA is 3.2, I completed 90 credits, "
                "and I expect an A in a 3-credit course. "
                "What will my new GPA be?"
            ),
            "session_id": "gpa-test",
        },
    )

    body = response.json()
    answer = body.get("answer", "")

    passed = (
        response.status_code == 200
        and "3.23" in answer
    )

    print_result(
        "GPA Tool",
        passed,
        f"Status: {response.status_code}\n"
        f"Answer:\n{answer}",
    )

    return passed


def test_study_schedule():
    response = client.post(
        "/chat",
        json={
            "question": (
                "Create a study schedule for these topics: "
                "Introduction, SQL, Normalization, Transactions. "
                "My exam is on 2026-09-10 and I can study "
                "3 hours per day."
            ),
            "session_id": "study-test",
        },
    )

    body = response.json()
    answer = body.get("answer", "")

    passed = (
        response.status_code == 200
        and len(answer.strip()) > 0
        and (
            "day" in answer.lower()
            or "schedule" in answer.lower()
        )
    )

    print_result(
        "Study Schedule Tool",
        passed,
        f"Status: {response.status_code}\n"
        f"Answer:\n{answer}",
    )

    return passed


def test_memory():
    session_id = "memory-test"

    first_response = client.post(
        "/chat",
        json={
            "question": "The database midterm is worth 25%.",
            "session_id": session_id,
        },
    )

    second_response = client.post(
        "/chat",
        json={
            "question": "How much is it worth?",
            "session_id": session_id,
        },
    )

    first_answer = first_response.json().get("answer", "")
    second_answer = second_response.json().get("answer", "")

    passed = (
        first_response.status_code == 200
        and second_response.status_code == 200
        and "25" in second_answer
    )

    print_result(
        "Conversation Memory",
        passed,
        f"First answer:\n{first_answer}\n\n"
        f"Follow-up answer:\n{second_answer}",
    )

    return passed


def test_empty_question():
    response = client.post(
        "/chat",
        json={
            "question": "",
            "session_id": "validation-test",
        },
    )

    body = response.json()
    answer = body.get("answer", "").lower()

    passed = (
        response.status_code == 200
        and "question" in answer
    )

    print_result(
        "Empty Question Handling",
        passed,
        f"Status: {response.status_code}\n"
        f"Response:\n{body}",
    )

    return passed


def main():
    print("\n" + "#" * 70)
    print("# UNIVERSITY COURSE & EXAM ASSISTANT")
    print("# FULL INTEGRATION TEST")
    print("#" * 70)

    results = [
        test_health(),
        test_rag(),
        test_grounding(),
        test_gpa(),
        test_study_schedule(),
        test_memory(),
        test_empty_question(),
    ]

    passed = sum(results)
    total = len(results)

    print("\n" + "#" * 70)
    print("# FINAL SUMMARY")
    print("#" * 70)
    print(f"Passed: {passed}/{total}")
    print(f"Failed: {total - passed}/{total}")

    if passed == total:
        print("\nALL TESTS PASSED")
    else:
        print("\nSOME TESTS FAILED")


if __name__ == "__main__":
    main()