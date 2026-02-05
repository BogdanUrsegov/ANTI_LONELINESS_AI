from aiogram import Router
from bot.modules.start import router as start_router


router = Router()
router.include_routers(start_router)


__all__ = ["router"]