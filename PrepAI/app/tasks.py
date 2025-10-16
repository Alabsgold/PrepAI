from sqlmodel import Session, select
from .database import engine
from .models import SourceDocument, GeneratedQuiz, GeneratedQuestion, GeneratedOption
from .worker import celery_app
from .services import DocumentService
from .ai_service import generate_quiz_questions_from_text


@celery_app.task
def process_document_task(document_id: int):
    with Session(engine) as session:
        try:
            statement = select(SourceDocument).where(SourceDocument.id == document_id)
            document = session.exec(statement).first()

            if not document:
                return {"status": "failed", "message": "Document not found"}

            document.status = "PROCESSING"
            session.add(document)
            session.commit()
            session.refresh(document)

            # Text Extraction
            doc_service = DocumentService(session=session)
            extracted_text = doc_service.extract_text_from_document(document.file_path)

            # Question Generation
            questions_data = generate_quiz_questions_from_text(extracted_text)

            # Save Quiz Data
            if questions_data:
                new_quiz = GeneratedQuiz(
                    title=f"Quiz for {document.original_filename}",
                    source_document_id=document.id
                )
                session.add(new_quiz)
                session.commit()
                session.refresh(new_quiz)

                for q_data in questions_data:
                    new_question = GeneratedQuestion(
                        question_text=q_data["question_text"],
                        quiz_id=new_quiz.id
                    )
                    session.add(new_question)
                    session.commit()
                    session.refresh(new_question)

                    for option_text in q_data["options"]:
                        is_correct = (option_text == q_data["correct_answer"])
                        new_option = GeneratedOption(
                            option_text=option_text,
                            is_correct=is_correct,
                            question_id=new_question.id
                        )
                        session.add(new_option)

                session.commit()

            document.status = "COMPLETED"
            session.add(document)
            session.commit()
            return {"status": "completed", "document_id": document_id}

        except Exception as e:
            # Rollback in case of error
            session.rollback()
            # Mark document as FAILED
            statement = select(SourceDocument).where(SourceDocument.id == document_id)
            document = session.exec(statement).first()
            if document:
                document.status = "FAILED"
                session.add(document)
                session.commit()
            # Optionally re-raise the exception to have it logged by Celery
            raise e