from typing import Any
import random
import string
from app.db.session import SessionLocal
from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr
from app import crud, models, schemas
from app import models, schemas
from app.api import deps
from app.utils import send_test_email

router = APIRouter()


@router.post("/test-email/", response_model=schemas.Msg, status_code=201)
def test_email(
        email_to: EmailStr,
        current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Test emails.
    """
    send_test_email(email_to=email_to)
    return {"msg": "Test email sent"}


def generate_random_pass(length):
    # With combination of lower and upper case
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    return result_str


def check_random_game_number(code):
    db = SessionLocal()
    ex_receive = crud.game.get_by_unique_number(db=db, unique_number=code)
    if ex_receive:
        code = random.randint(1, 99999)
        check_random_game_number(code=code)
    else:
        return code
