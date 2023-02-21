import logging
from typing import Any, Dict, List
from app.constants.role import Role
from app import crud, schemas, models
from app.api import deps
from app.schemas.search import FilterRuleType, Search, SearchResponse
from fastapi import APIRouter, Body, Depends, HTTPException, Security, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
import random
from random import *
from app.api.api_v1.endpoints.utils import check_random_game_number

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[schemas.Game])
def read_games(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"], Role.GUEST["name"]],
        )
) -> Any:
    """
    Retrieve games.
    """
    games = crud.game.get_multi(db, skip=skip, limit=limit, user_id=current_user.id)

    return games


@router.post("/search", response_model=SearchResponse[schemas.Game])
async def search_game(
        *, db: Session = Depends(deps.get_db), search_params: Search,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"], Role.GUEST["name"]],
        )
) -> Any:
    """
    Search in games.
    """
    try:
        rules: Dict[FilterRuleType] = jsonable_encoder(search_params)["filter"]
        rules["rules"].append(
            {
                "field": "user_id",
                "operator": "equal",
                "value": current_user.id,
            }
        )

        total, games = crud.game.search(
            db,
            rules=rules,
            page_number=search_params.page_number,
            page_size=search_params.page_size,
        )

        return SearchResponse[schemas.Game](result=games, total=total)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/create",
    response_model=schemas.Game,
)
async def create_game(
        db: Session = Depends(deps.get_db),
        *,
        game_in: schemas.GameCreate,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"], Role.GUEST["name"]],
        )

) -> Any:
    """
    Create new Game.
    """
    code = randint(1, 9999)
    code = check_random_game_number(code=code)

    try:
        game = crud.game.create(db=db, obj_in=game_in, user_id=current_user.id, unique_number=code)
        return game
    except Exception as e:
        logger.error(e)
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post(
    "/play",
    response_model=schemas.ShowGame,
)
async def play_game(
        db: Session = Depends(deps.get_db),
        *,
        game_in: schemas.PlayGame,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"], Role.GUEST["name"]],
        )

) -> Any:
    """
    Play created Game by user.
    """
    games = crud.game.get_by_unique_number(db=db, unique_number=game_in.game_unique_number)
    if len(games) > 6:
        raise HTTPException(status_code=400, detail="this game is finished")

    game_obj_in = {"name": game_in.name, "game_unique_number": game_in.game_unique_number}
    game = crud.game.create(db=db, obj_in=game_obj_in, user_id=current_user.id)

    if len(games) == 5:
        game.status = "FINISHED"
        db.add(game)
        db.commit()

    questions = crud.question.get_multi(db)
    random_question = random.choice(questions)
    game.questions = random_question
    db.add(game)
    db.commit()

    #    random_question.game_id = game.id

    correct_option = random_question.answers
    answers_list = [n for n in crud.answer.get_multi(db)]
    answers_choice = answers_list.remove(correct_option)
    option1 = random.choice(answers_choice)
    answers_choice = answers_list.remove(option1)
    option2 = random.choice(answers_choice)
    answers_choice = answers_list.remove(option2)
    option3 = random.choice(answers_choice)
    return schemas.ShowGame(game_id=game.id, question_id=random_question.id,question_detail=random_question.detail, currect_option=correct_option.detail,
                            option1=option1.detail, option2=option2.detail,
                            option3=option3.detail).dict()


@router.post(
    "/send_answer",
    response_model=schemas.ShowResult,
)
async def send_answer_game(
        db: Session = Depends(deps.get_db),
        *,
        game_in: schemas.SendAnswerGame,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"], Role.GUEST["name"]],
        )

) -> Any:
    """
    Send response Answered by user.
    """
    game = crud.game.get_by_id(db=db,game_id=game_in.game_id)
    question = crud.question.get_by_id(db=db,question_id=game_in.question_id)
    user_answer = crud.answer.get_by_detail(db=db,detail=game_in.user_answer_detail)
    game.user_answer_id = user_answer.id
    db.add(game)
    db.commit()
    if question.correct_answer == user_answer.detail:
        game.point = question.point
        db.add(game)
        db.commit()
        return schemas.ShowGame(message="your answer is correct",point=question.point)
    else:
        return schemas.ShowGame(message="your answer is wrong",point=0,currect_option=question.correct_answer)




@router.delete("/{id}", response_model=schemas.Game)
def delete_game(
        *,
        db: Session = Depends(deps.get_db),
        id: str,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"]],
        )
) -> Any:
    """
    Delete a game.
    """
    game = crud.game.get(db=db, id=id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    game = crud.game.remove(db=db, id=id)
    return game
