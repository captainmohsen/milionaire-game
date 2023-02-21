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


@router.get("/", response_model=List[schemas.Answer])
def read_answers(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"]],
        )
) -> Any:
    """
    Retrieve answers.
    """
    answers = crud.answer.get_multi(db, skip=skip, limit=limit)

    return answers


@router.post("/search", response_model=SearchResponse[schemas.Answer])
async def search_answer(
        *, db: Session = Depends(deps.get_db), search_params: Search,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"]],
        )
) -> Any:
    """
    Search in answers.
    """
    try:
        rules: Dict[FilterRuleType] = jsonable_encoder(search_params)["filter"]

        total, answers = crud.answer.search(
            db,
            rules=rules,
            page_number=search_params.page_number,
            page_size=search_params.page_size,
        )

        return SearchResponse[schemas.Question](result=answers, total=total)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/create",
    response_model=schemas.Answer,
)
async def create_answer(
        db: Session = Depends(deps.get_db),
        *,
        answer_in: schemas.AnswerCreate,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"]],
        )

) -> Any:
    """
    Create new Answer.
    """
    answer = crud.answer.get_by_detail(db=db, detail=answer_in.detail)
    if answer:
        raise HTTPException(
            status_code=400,
            detail="The answer with this detail already exists in the system.",
        )

    answer = crud.answer.get_by_question_id(db=db, detail=answer_in.question_id)
    if answer:
        raise HTTPException(
            status_code=400,
            detail="The answer with this question already exists in the system.",
        )
    try:
        answer = crud.answer.create(db=db, obj_in=answer_in)
        return answer
    except Exception as e:
        logger.error(e)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{id}", response_model=schemas.Answer)
def delete_answer(
        *,
        db: Session = Depends(deps.get_db),
        id: str,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"]],
        )
) -> Any:
    """
    Delete an answer.
    """
    answer = crud.answer.get(db=db, id=id)
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    answer = crud.answer.remove(db=db, id=id)
    return answer
