from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.event import Event, EventRSVP
from models.quiz import QuizTemplate, QuizQuestion, QuizAttempt, QuizResponse, QuizOption
from models.student import Student
from services.quiz_scoring import compute_quiz_result
from datetime import datetime
from services.auth import get_current_user 
from schemas.quiz import QuizOut, QuizSubmit


router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.get("/event/{event_id}", response_model=list[QuizOut])
def get_quiz(
    event_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    student_id = current_user.id

    # CHECK 1: has student RSVPed to this event?
    rsvp = db.query(EventRSVP).filter(
        EventRSVP.event_id == event_id,
        EventRSVP.student_id == student_id
    ).first()

    if not rsvp:
        raise HTTPException(status_code=403, detail="You have not registered for this event")

    # CHECK 2: does event exist?
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # CHECK 3: is event cancelled?
    if event.status == "cancelled":
        raise HTTPException(status_code=400, detail="Event is cancelled")

    # get all quiz templates for this event in sequence order
    quizzes = db.query(QuizTemplate).filter(
        QuizTemplate.event_id == event_id
    ).order_by(QuizTemplate.sequence_no).all()

    if not quizzes:
        raise HTTPException(status_code=404, detail="No quizzes found for this event")

    # get questions and options for each quiz
    result = []
    for quiz in quizzes:
        questions = db.query(QuizQuestion).filter(
            QuizQuestion.quiz_template_id == quiz.id
        ).order_by(QuizQuestion.question_no).all()

        questions_data = []
        for question in questions:
            options = db.query(QuizOption).filter(
                QuizOption.option_set_id == question.option_set_id
            ).order_by(QuizOption.display_order).all()

            questions_data.append({
                "id": str(question.id),
                "question_no": question.question_no,
                "question_text": question.question_text,
                "area_code": question.area_code,
                "form": question.form,
                "option_set_id": str(question.option_set_id),  # missing!
                "quiz_template_id": str(quiz.id),    
                "options": [
                    {
                        "id": str(opt.id),
                        "option_set_id": str(opt.option_set_id), 
                        "option_text": opt.option_text,
                        "score_value": opt.score_value,
                        "display_order": opt.display_order
                    }
                    for opt in options
                ]
            })

        result.append({
            "quiz_template_id": str(quiz.id),
            "quiz_type": quiz.quiz_type,
            "title": quiz.title,
            "sequence_no": quiz.sequence_no,
            "questions": questions_data
        })

    return result


@router.post("/submit")
def submit_quiz(
    data: QuizSubmit,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    student_id = current_user.id

    quiz_template_id = data.quiz_template_id
    answers = data.answers

    # CHECK 1: does quiz template exist?
    quiz = db.query(QuizTemplate).filter(
        QuizTemplate.id == quiz_template_id
    ).first()

    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    # CHECK 2: has student already submitted this quiz?
    existing_attempt = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_template_id == quiz_template_id,
        QuizAttempt.student_id == student_id,
        QuizAttempt.status == "submitted"
    ).first()

    if existing_attempt:
        raise HTTPException(status_code=400, detail="You have already submitted this quiz")

    # CHECK 3: has student RSVPed to this event?
    rsvp = db.query(EventRSVP).filter(
        EventRSVP.event_id == quiz.event_id,
        EventRSVP.student_id == student_id
    ).first()

    if not rsvp:
        raise HTTPException(status_code=403, detail="You have not registered for this event")

    # get student gender for GWBS scoring
    student = db.query(Student).filter(Student.id == student_id).first()
    gender = student.gender if student else "male"

    # compute result using existing scoring service
    result_json = compute_quiz_result(
        quiz_type=quiz.quiz_type,
        answers=answers,
        gender=gender
    )

    # get or create attempt
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_template_id == quiz_template_id,
        QuizAttempt.student_id == student_id
    ).first()

    if attempt:
        # update existing attempt
        attempt.status = "submitted"
        attempt.attempted_at = datetime.now()
        attempt.total_score = result_json.get("total_score")
        attempt.overall_remark = result_json.get("interpretation")
        attempt.result_json = result_json
    else:
        # create new attempt
        attempt = QuizAttempt(
            quiz_template_id=quiz_template_id,
            student_id=student_id,
            status="submitted",
            attempted_at=datetime.now(),
            total_score=result_json.get("total_score"),
            overall_remark=result_json.get("interpretation"),
            result_json=result_json
        )
        db.add(attempt)

    db.commit()
    db.refresh(attempt)

    # save individual responses
    for question_id, selected_option_id in answers.items():
        # get score for selected option
        option = db.query(QuizOption).filter(
            QuizOption.id == selected_option_id
        ).first()

        score_awarded = option.score_value if option else 0

        response = QuizResponse(
            attempt_id=attempt.id,
            question_id=question_id,
            selected_option_id=selected_option_id,
            score_awarded=score_awarded
        )
        db.add(response)

    db.commit()

    return {
        "message": "Quiz submitted successfully",
        "attempt_id": str(attempt.id),
        "result": result_json
    }


@router.get("/{attempt_id}/result")
def get_quiz_result(
    attempt_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    student_id = current_user.id

    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.id == attempt_id,
        QuizAttempt.student_id == student_id,
        QuizAttempt.status == "submitted"
    ).first()

    if not attempt:
        raise HTTPException(status_code=404, detail="Result not found")

    quiz = db.query(QuizTemplate).filter(
        QuizTemplate.id == attempt.quiz_template_id
    ).first()

    return {
        "quiz_type": quiz.quiz_type,
        "title": quiz.title,
        "attempted_at": attempt.attempted_at,
        "total_score": attempt.total_score,
        "overall_remark": attempt.overall_remark,
        "result_json": attempt.result_json
    }