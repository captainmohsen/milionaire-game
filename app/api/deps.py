from typing import Any, Dict, Generator,Optional
import logging
from app.core import security
from fastapi import Depends, HTTPException, Security, status,Body
from app.constants.role import Role
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token",
    scopes={
        Role.GUEST["name"]: Role.GUEST["description"],
        Role.ADMIN["name"]: Role.ADMIN["description"],
    },
)


def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


def get_current_user(
        security_scopes: SecurityScopes,
        db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )

        id: str = payload.get("id")
        if id is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        logger.info(payload)

        token_data = schemas.TokenPayload(scopes=token_scopes, id=id)
        logger.info(token_data.scopes)
    except (jwt.JWTError, ValidationError):
        raise credentials_exception
    user = crud.user.get(db, id=token_data.id)
    logger.info("*******")
    logger.info(security_scopes.scopes)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    #   for scope in security_scopes.scopes:
    for scope in token_data.scopes:
        # if scope not in token_data.scopes:
        if scope not in security_scopes.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    # if security_scopes.scopes and not token_data.role:
    #     raise HTTPException(
    #         status_code=401,
    #         detail="Not enough permissions",
    #         headers={"WWW-Authenticate": authenticate_value},
    #     )
    # if (
    #         security_scopes.scopes
    #         and token_data.role not in security_scopes.scopes
    # ):
    #     raise HTTPException(
    #         status_code=401,
    #         detail="Not enough permissions",
    #         headers={"WWW-Authenticate": authenticate_value},
    #     )
    return user


# def get_current_active_user(
#     current_user: models.User = Depends(get_current_user),
# ) -> models.User:
#     if not crud.user.is_active(current_user):
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


def get_current_active_user(
        current_user: models.User = Security(get_current_user, scopes=[], ),
) -> models.User:
    if not crud.user.is_active(current_user):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user




