import time
from sqlmodel import Session, select
from .database import engine
from .models import SourceDocument
from .worker import celery_app


@celery_app.task
def process_document_task(document_id: int):
    with Session(engine) as session:
        statement = select(SourceDocument).where(SourceDocument.id == document_id)
        document = session.exec(statement).first()

        if not document:
            # Handle case where document is not found
            return {"status": "failed", "message": "Document not found"}

        document.status = "PROCESSING"
        session.add(document)
        session.commit()

        time.sleep(30)

        document.status = "COMPLETED"
        session.add(document)
        session.commit()
    return {"status": "completed", "document_id": document_id}