from .message import router as message_router
from aiogram import Router


router = Router()

router.include_routers(message_router)


__all__ = [
    "message_router"
]