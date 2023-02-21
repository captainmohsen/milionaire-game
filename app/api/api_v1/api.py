from app.api.api_v1.endpoints import login, answer, game, users,question
from fastapi import APIRouter


api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(game.router, prefix="/games", tags=["games"])
api_router.include_router(question.router, prefix="/questions", tags=["questions"])
api_router.include_router(answer.router, prefix="/answers", tags=["answers"])
