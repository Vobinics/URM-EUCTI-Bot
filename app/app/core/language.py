from aiogram.contrib.middlewares.i18n import I18nMiddleware
from app.core.bot import dp
from app.core.config import BASE_DIR

I18N_DOMAIN = 'bot'

LOCALES_DIR = BASE_DIR / 'locales'

# Setup i18n middleware
i18n = I18nMiddleware(I18N_DOMAIN, LOCALES_DIR)
dp.middleware.setup(i18n)

# Alias for gettext method
_ = i18n.gettext
