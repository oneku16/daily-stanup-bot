from aiogram import Router

from app.interface.handlers import admin, standup, user

router = Router()
router.include_router(user.router)
router.include_router(standup.router)
router.include_router(admin.router)

__all__ = ["router"]
