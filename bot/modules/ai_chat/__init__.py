from .handlers import router as handlers_router
from aiogram import Router


router = Router()

router.include_routers(handlers_router)


__all__ = [
    "handlers_router"
]