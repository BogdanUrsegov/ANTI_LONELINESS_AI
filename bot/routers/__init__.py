from aiogram import Router
from bot.modules.greeting import router as start_router
from bot.modules.age_gate import router as age_gate_router
from bot.modules.archetype import router as archetype_router
from bot.modules.mini_form import router as mini_form_router
from bot.modules.settings_time import router as settings_time_router
from bot.modules.main_menu import router as main_menu_router
from bot.modules.ai_chat import router as ai_chat_router




router = Router()
router.include_routers(start_router, 
                       age_gate_router, 
                       archetype_router, 
                       mini_form_router, 
                       settings_time_router, 
                       main_menu_router, 
                       ai_chat_router)


__all__ = ["router"]