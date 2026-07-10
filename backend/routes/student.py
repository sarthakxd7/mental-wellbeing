from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.event import Event, EventRSVP
from models.student import Student
from models.quiz import QuizAttempt, QuizTemplate
from schemas.event import EventOut, EventRSVPCreate
from schemas.student import DashboardOut
from services.auth import get_current_user
from schemas.quiz import QuizAttemptOut

router = APIRouter(prefix="/student", tags=["student"])


@router.get("/events", response_model=list[EventOut])
def get_events(
    status: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    valid_statuses = ["upcoming", "completed", "postponed"]

    if status and status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status. Choose from upcoming, completed, postponed")

    if status:
        events = db.query(Event).filter(Event.status == status).all()
    else:
        events = db.query(Event).filter(Event.status != "cancelled").all()

    return events


@router.post("/rsvp")
def rsvp_event(
    data: EventRSVPCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    # CHECK 1: already RSVPed?
    existing_rsvp = db.query(EventRSVP).filter(
        EventRSVP.event_id == data.event_id,
        EventRSVP.student_id == current_user.id
    ).first()

    if existing_rsvp:
        raise HTTPException(status_code=400, detail="Already RSVPed")

    # CHECK 2: event exists?
    event = db.query(Event).filter(Event.id == data.event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # CHECK 3: event cancelled?
    if event.status == "cancelled":
        raise HTTPException(status_code=400, detail="Event is cancelled")

    new_rsvp = EventRSVP(
        event_id=data.event_id,
        student_id=current_user.id
    )
    db.add(new_rsvp)
    db.commit()

    return {"message": "RSVP successful"}


@router.get("/rsvps", response_model=list[EventOut])
def get_rsvps(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    events = db.query(Event).join(EventRSVP).filter(
        EventRSVP.student_id == current_user.id
    ).all()

    return events


@router.get("/dashboard", response_model=DashboardOut)
def show_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    info = db.query(Student).filter(Student.id == current_user.id).first()

    if not info:
        raise HTTPException(status_code=404, detail="Student not found")

    total_rsvps = db.query(EventRSVP).filter(
        EventRSVP.student_id == current_user.id
    ).count()

    total_quizzes = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == current_user.id
    ).count()

    return {
        "student": info,
        "summary": {
            "total_rsvps": total_rsvps,
            "total_quizzes": total_quizzes
        }
    }


@router.get("/results", response_model=list[QuizAttemptOut])
def get_results(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    results = db.query(QuizAttempt).filter(
        QuizAttempt.student_id == current_user.id,
        QuizAttempt.status == "submitted"
    ).all()

    return results

@router.get("/events/{event_id}/quizzes")
def get_quizzes_for_event(
    event_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    # Check if the student has RSVPed for the event
    rsvp = db.query(EventRSVP).filter(
        EventRSVP.event_id == event_id,
        EventRSVP.student_id == current_user.id
    ).first()

    if not rsvp:
        raise HTTPException(status_code=403, detail="You have not RSVPed for this event")

    # Fetch quizzes associated with the event
    quizzes = db.query(QuizAttempt, QuizTemplate).join(
    QuizTemplate, QuizAttempt.quiz_template_id == QuizTemplate.id).filter(
    QuizTemplate.event_id == event_id,
    QuizAttempt.student_id == current_user.id,  
    QuizAttempt.status == "submitted").all()
    
    
    result = []
    for attempt, quiz in quizzes:
        if quiz.quiz_type in ["SCQ", "GWBS"]:
           score_display = f"Score {attempt.total_score}"
           interpretation = attempt.result_json.get("interpretation")
        elif quiz.quiz_type == "TABBPS":
           score_display = attempt.result_json.get("final_classification")
           interpretation = None
        elif quiz.quiz_type == "EI":
           interps = attempt.result_json.get("competency_interpretations", {})
           strengths = sum(1 for v in interps.values() if v == "Strength")
           score_display = f"{strengths} Strengths"
           interpretation = None

        result.append({
            "quiz_type": quiz.quiz_type,
            "title": quiz.title,
            "score_display": score_display,
            "interpretation": interpretation })

    return result

@router.get("/events/{event_id}/overall")
def get_event_overall_results(
    event_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Not authorized")

    # check RSVP
    rsvp = db.query(EventRSVP).filter(
        EventRSVP.event_id == event_id,
        EventRSVP.student_id == current_user.id
    ).first()

    if not rsvp:
        raise HTTPException(status_code=403, detail="You have not RSVPed for this event")

    # get event details
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # get all quiz attempts for this event
    quizzes = db.query(QuizAttempt, QuizTemplate).join(
        QuizTemplate, QuizAttempt.quiz_template_id == QuizTemplate.id
    ).filter(
        QuizTemplate.event_id == event_id,
        QuizAttempt.student_id == current_user.id,
        QuizAttempt.status == "submitted"
    ).order_by(QuizTemplate.sequence_no).all()

    quiz_results = []
    for attempt, quiz in quizzes:
        quiz_results.append({
            "quiz_type": quiz.quiz_type,
            "title": quiz.title,
            "result": attempt.result_json
        })

    return {
        "event_title": event.title,
        "event_date": event.event_date,
        "quizzes": quiz_results
    }