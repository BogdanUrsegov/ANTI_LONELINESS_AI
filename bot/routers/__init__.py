from aiogram import Router
from bot.modules.greeting import router as start_router
from bot.modules.age_gate import router as age_gate_router
from bot.modules.archetype import router as archetype_router


router = Router()
router.include_routers(start_router, age_gate_router, archetype_router)


__all__ = ["router"]