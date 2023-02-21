from typing import Any, List

from app.constants.role import Role
from fastapi import APIRouter, Body, Depends, HTTPException, Security
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session
import logging
from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.utils import send_new_account_email
from app.models.user_role import UserRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
        db: Session = Depends(deps.get_db),
        skip: int = 0,
        limit: int = 100,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"], Role.GUEST["name"]],
        ),
) -> Any:
    """
    Retrieve users.
    """
    users = crud.user.get_multi(db, skip=skip, limit=limit)
    return users


@router.post("/", response_model=schemas.User)
def create_user(
        *,
        db: Session = Depends(deps.get_db),
        user_in: schemas.UserCreate,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"]],
        ),
) -> Any:
    """
    Create new user.
    """
    user = crud.user.get_by_phone(db, phone=user_in.phone_number)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    logger.info(user_in)
    user = crud.user.create(db, obj_in=user_in)
    role = crud.role.get_by_name(db, name=user_in.role)
    user_role_in = schemas.UserRoleCreate(adminuser_id=user.id, role_id=role.id)
    crud.user_role.create(db, obj_in=user_role_in)
    # if settings.EMAILS_ENABLED and user_in.email:
    #     send_new_account_email(
    #         email_to=user_in.email, username=user_in.email, password=user_in.password
    #     )
    user.role = user_in.role
 #   user.scope_access = user_in.scope_access
    return user


@router.get("/{user_id}", response_model=schemas.UserResponse)
def read_user_by_id(
        user_id: str,
        db: Session = Depends(deps.get_db),

        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"]],
        ),
) -> Any:
    """
    Get a specific user by id.
    """
    user_obj = crud.user.get(db, id=user_id)
    response = schemas.UserResponse.from_orm(user_obj)

    # if user == current_user:
    #     return user
    # if not crud.user.is_superuser(current_user):
    #     raise HTTPException(
    #         status_code=400, detail="The user doesn't have enough privileges"
    #     )
    return response


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
        *,
        db: Session = Depends(deps.get_db),
        user_id: str,
        user_in: schemas.UserUpdate,
        current_user: models.User = Security(
            deps.get_current_active_user,
            scopes=[Role.ADMIN["name"]],
        ),
) -> Any:
    """
    Update a user.
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system",
        )
    user = crud.user.update(db, db_obj=user, obj_in=user_in)

    role = crud.role.get_by_name(db, name=user_in.role)
    logger.info(role.id)
    # To Do : modify this part with Crud
    user_role = db.query(UserRole).filter(UserRole.adminuser_id == user.id).first()
    user_role.role_id = role.id
    db.add(user_role)
    db.commit()
    user_role_in = schemas.UserRoleUpdate(adminuser_id=user.id, role_id=role.id)

    return user
