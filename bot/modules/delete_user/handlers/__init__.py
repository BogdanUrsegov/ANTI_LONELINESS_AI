from .commands import router as commands_router
from aiogram import Router


router = Router()

router.include_router(commands_router)

__all__ = [
    "router"
]