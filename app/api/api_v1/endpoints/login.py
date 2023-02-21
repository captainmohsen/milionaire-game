from datetime import timedelta
from typing import Any
import logging
from app.constants.role import Role

from fastapi import APIRouter, Body, Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.utils import (
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
)
from app.models.user import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login/access-token", response_model=schemas.Token)
def login_access_token(
        db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.user.authenticate(
        db, phone=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect phone or password")
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    role = user.user_role.role.name
    logger.info(role)
    if not user.user_role:
        role = "GUEST"
    else:
        role = user.user_role.role.name
        logger.info(role)
    token_payload = {
        "id": str(user.id),
        "scopes": form_data.scopes

    }

    return {
        "access_token": security.create_access_token(
            token_payload, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login/test-token", response_model=schemas.UserResponse)
def test_token(db: Session = Depends(deps.get_db), current_user: models.User = Security(
    deps.get_current_active_user,
    scopes=[Role.ADMIN["name"]],
), ) -> Any:
    """
    Test access token
    """
    adminuser_obj = db.query(User).order_by(User.created_at.desc()).first()
    response = schemas.UserResponse.from_orm(adminuser_obj)
    # return current_user
    return response


# @router.post("/password-recovery/{phone}", response_model=schemas.Msg)
# def recover_password(email: str, db: Session = Depends(deps.get_db)) -> Any:
#     """
#     Password Recovery
#     """
#     user = crud.user.get_by_phone(db, email=email)
#
#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="The user with this username does not exist in the system.",
#         )
#     password_reset_token = generate_password_reset_token(phone=email)
#     send_reset_password_email(
#         email_to=user.email, email=email, token=password_reset_token
#     )
#     return {"msg": "Password recovery email sent"}


@router.post("/login/reset-password", response_model=schemas.Msg)
def reset_password(
    token: str = Body(...),
    oldPassword: str = Body(...),
    newPassword: str = Body(
        ..., regex="^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$"
    ),
    db: Session = Depends(deps.get_db),
    current_user: models.user = Depends(deps.get_current_active_user),
) -> Any:
    """
    Reset password
    """
    user_id = verify_password_reset_token(token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not crud.user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    if not verify_password(oldPassword, user.hashed_password):
        raise HTTPException(
            status_code=400,
            detail="The old password is incorrect",
        )
    hashed_password = get_password_hash(newPassword)

    user.hashed_password = hashed_password
    db.add(user)
    db.commit()
    return {"msg": "Password updated successfully"}

