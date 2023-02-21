from app import crud, schemas
from app.core.config import settings
from app.constants.role import Role
import logging
from sqlalchemy.orm import Session

from app.db.seeder import *  # noqa: F401

logger = logging.getLogger(__name__)


def init_db(db: Session) -> None:
    userSeed = UserSeed(
        db=db,
        data=[
            {
                "phone_number": "09122223456",
                "national_id": "1000009009",
                "is_active": True,
                "password": "root1234",
            },

        ],
    )
    logger.info(f"initilize Users data seeder!")
    userSeed.proceed()
    logger.info(f"Users data seeder done!")


    # Create 1st Superuser
    user = crud.user.get_by_email(db, email=settings.FIRST_SUPER_ADMIN_EMAIL)
    if not user:
        user_in = schemas.UserCreate(
            phone_number=settings.FIRST_SUPER_ADMIN_PHONE,
            password=settings.FIRST_SUPER_ADMIN_PASSWORD,
            full_name=settings.FIRST_SUPER_ADMIN_FULL_NAME,
        )
        user = crud.user.create(db, obj_in=user_in)

    # Create Role If They Don't Exist
    guest_role = crud.role.get_by_name(db, name=Role.GUEST["name"])
    if not guest_role:
        guest_role_in = schemas.RoleCreate(
            name=Role.GUEST["name"], description=Role.GUEST["description"]
        )
        crud.role.create(db, obj_in=guest_role_in)
    admin_role = crud.role.get_by_name(db, name=Role.ADMIN["name"])
    if not admin_role:
        admin_role_in = schemas.RoleCreate(
            name=Role.ADMIN["name"], description=Role.ADMIN["description"]
        )
        crud.role.create(db, obj_in=admin_role_in)


