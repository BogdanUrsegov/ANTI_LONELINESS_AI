from aiogram import Router
from bot.modules.greeting import router as start_router
from bot.modules.age_gate import router as age_gate_router
from bot.modules.archetype import router as archetype_router
from bot.modules.mini_form import router as mini_form_router
from bot.modules.settings_time import router as settings_time_router
from bot.modules.main_menu import router as main_menu_router
from bot.modules.ai_chat import router as ai_chat_router
from bot.modules.frequency_messages import router as frequency_messages_router
from bot.modules.about_product import router as about_product_router
from bot.modules.delete_user import router as delete_user_router
from bot.modules.clear_memory import router as clear_memory_router
from bot.modules.pause import router as pause_router
from bot.modules.subscription import router as subscription_router


router = Router()
router.include_routers(start_router,
                       delete_user_router,
                       main_menu_router,
                       age_gate_router, 
                       archetype_router, 
                       mini_form_router, 
                       settings_time_router, 
                       ai_chat_router,
                       frequency_messages_router,
                       about_product_router,
                       clear_memory_router,
                       pause_router,
                        subscription_router
                       )


__all__ = ["router"]