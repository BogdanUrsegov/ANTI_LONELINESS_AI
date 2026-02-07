from aiogram import Router
from bot.modules.greeting import router as start_router
from bot.modules.age_gate import router as age_gate_router
from bot.modules.archetype import router as archetype_router
from bot.modules.mini_form import router as mini_form_router
from bot.modules.settings_time import router as settings_time_router




router = Router()
router.include_routers(start_router, age_gate_router, archetype_router, mini_form_router, settings_time_router)


__all__ = ["router"]