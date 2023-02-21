import logging
from typing import Any, Dict, List
from app.constants.role import Role
from app import crud, schemas, models
from app.api import deps
from app.schemas.search import FilterRuleType, Search, SearchResponse
from fastapi import APIRouter, Body, Depends, HTTPException, Security, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[schemas.Question])
def read_questions(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"]],
        )
) -> Any:
    """
    Retrieve questions.
    """
    questions = crud.question.get_multi(db, skip=skip, limit=limit)

    return questions


@router.post("/search", response_model=SearchResponse[schemas.Question])
async def search_question(
        *, db: Session = Depends(deps.get_db), search_params: Search,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"]],
        )
) -> Any:
    """
    Search in questions.
    """
    try:
        rules: Dict[FilterRuleType] = jsonable_encoder(search_params)["filter"]

        total, questions = crud.question.search(
            db,
            rules=rules,
            page_number=search_params.page_number,
            page_size=search_params.page_size,
        )

        return SearchResponse[schemas.Question](result=questions, total=total)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/create",
    response_model=schemas.Question,
)
async def create_question(
        db: Session = Depends(deps.get_db),
        *,
        question_in: schemas.QuestionCreate,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"]],
        )

) -> Any:
    """
    Create new Question.
    """

    question = crud.question.get_by_detail(db=db, detail=question_in.detail)
    if question:
        raise HTTPException(
            status_code=400,
            detail="The question with this detail already exists in the system.",
        )

    try:
        question = crud.question.create(db=db, obj_in=question_in)
        answer_obj_in = {"detail": question_in.correct_answer, "question_id": question.id}
        answer = crud.answer.create(db=db, obj_in=answer_obj_in)
        question.answers = answer
        db.add(question)
        db.commit()
        return question
    except Exception as e:
        logger.error(e)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{id}", response_model=schemas.Question)
def delete_question(
        *,
        db: Session = Depends(deps.get_db),
        id: str,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"]],
        )
) -> Any:
    """
    Delete a question.
    """
    question = crud.question.get(db=db, id=id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    question = crud.question.remove(db=db, id=id)
    return question
