from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.event import Event, EventReport, EventRSVP
from models.student import Student
from models.quiz import QuizTemplate, QuizAttempt
from services.auth import require_role 
from schemas.event import EventReportOut
from models.admin import Admin  

router = APIRouter(prefix="/superuser", tags=["superuser"])


@router.get("/events")
def get_all_events(
    status: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("superuser"))
):
    

    valid_statuses = ["upcoming", "completed", "postponed", "cancelled"]

    if status and status not in valid_statuses:
        raise HTTPException(status_code=400, detail="Invalid status. Choose from upcoming, completed, postponed")

    query = db.query(Event, Admin.name.label("admin_name"))\
        .join(Admin, Event.admin_id == Admin.id)

    if status:
        query = query.filter(Event.status == status)
    else:
        query = query.filter(Event.status != "cancelled")

    events = query.all()

    return [
        {
            "id": str(event.id),
            "title": event.title,
            "venue": event.venue,
            "event_date": event.event_date,
            "event_time": event.event_time,
            "status": event.status,
            "description": event.description,
            "admin_name": admin_name
        }
        for event, admin_name in events
    ]


@router.get("/events/{event_id}/results")
def get_event_results(
    event_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("superuser"))
):
    
    
    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    results = db.query(QuizAttempt, Student, QuizTemplate)\
        .join(QuizTemplate, QuizAttempt.quiz_template_id == QuizTemplate.id)\
        .join(Student, QuizAttempt.student_id == Student.id)\
        .filter(
            QuizTemplate.event_id == event_id,
            QuizAttempt.status == "submitted"
        ).all()

    return [
        {
            "student_name": student.name,
            "enrollment_no": student.enrollment_no,
            "quiz_type": quiz_template.quiz_type,
            "total_score": attempt.total_score,
            "result_json": attempt.result_json,
            "attempted_at": attempt.attempted_at
        }
        for attempt, student, quiz_template in results
    ]


@router.get("/events/{event_id}/report", response_model=EventReportOut)
def get_event_report(
    event_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("superuser"))
):
    

    event = db.query(Event).filter(Event.id == event_id).first()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    report = db.query(EventReport).filter(
        EventReport.event_id == event_id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="No report uploaded for this event")

    return report


@router.get("/students")
def get_all_students(
    db: Session = Depends(get_db),
    current_user = Depends(require_role("superuser"))
):
    

    students = db.query(Student).all()

    result = []
    for student in students:
        events_count = db.query(EventRSVP).filter(
            EventRSVP.student_id == student.id
        ).count()

        quizzes_count = db.query(QuizAttempt).filter(
            QuizAttempt.student_id == student.id,
            QuizAttempt.status == "submitted"
        ).count()

        result.append({
            "name": student.name,
            "email": student.email,
            "enrollment_no": student.enrollment_no,
            "course": student.course,
            "semester": student.semester,
            "events_participated": events_count,
            "quizzes_completed": quizzes_count
        })

    return result


@router.get("/dashboard")
def get_superuser_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(require_role("superuser"))
):
    

    # TODO: finalize after team discussion
    # basic summary for now

    total_students = db.query(Student).count()
    total_events = db.query(Event).count()
    total_admins = db.query(Admin).count()
    total_quizzes_completed = db.query(QuizAttempt).filter(
        QuizAttempt.status == "submitted"
    ).count()

    return {
        "summary": {
            "total_students": total_students,
            "total_events": total_events,
            "total_admins": total_admins,
            "total_quizzes_completed": total_quizzes_completed
        }
        # TODO: add filtered results (need_attention, average, good)
        # after team confirms classification logic
    }