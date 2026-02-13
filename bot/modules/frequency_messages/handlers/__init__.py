from .callbacks import router as callbacks_router
from aiogram import Router


router = Router()

router.include_router(callbacks_router)


__all__ = [
    "router"
]