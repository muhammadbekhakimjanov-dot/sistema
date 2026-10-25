import os
from pathlib import Path
from dotenv import load_dotenv

# Лойиҳанинг энг ташқари илдизи (madrasah-system)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-your-secret-key-here-change-this")
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = ['sistema-16gr.onrender.com', 'localhost', '127.0.0.1']

INSTALLED_APPS = [
    "jazzmin",  # Админ панелни замонавий қилиш учун (энг бошида туриши шарт)
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "madrasah.accounts.apps.AccountsConfig",
    "madrasah.core.apps.CoreConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "madrasah.accounts.middleware.ForcePasswordChangeMiddleware",
]

ROOT_URLCONF = "madrasah.config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "madrasah" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "madrasah.core.context_processors.menu",
            ]
        },
    }
]

WSGI_APPLICATION = "madrasah.config.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ky"
TIME_ZONE = "Asia/Bishkek"
USE_I18N = True
USE_TZ = True
LANGUAGES = [("ky", "Кыргызча"), ("uz", "Ozbekcha"), ("ru", "Русский")]
LOCALE_PATHS = [BASE_DIR / "locale"]

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

SESSION_COOKIE_AGE = 60 * 60 * 8  # 8 соат

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True


# ==========================================
# JAZZMIN (Замонавий Админ Панель Созламалари)
# ==========================================
JAZZMIN_SETTINGS = {
    "site_title": "Имам Аль-Бухарий",
    "site_header": "Имам Аль-Бухарий Медресеси",
    "site_brand": "Имам Аль-Бухарий",
    "welcome_sign": "Имам Аль-Бухарий медресеси бошқарув панелига хуш келибсиз!",
    "copyright": "Имам Аль-Бухарий Медресеси",
    "search_model": "core.Student",
    "topmenu_links": [
        {"name": "Бош саҳифа", "url": "admin:index", "permissions": ["auth.view_user"]},
        {"name": "Сайтга ўтиш", "url": "/", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "accounts.User": "fas fa-users-cog",
        "accounts.UserProfile": "fas fa-user-tag",
        "core.Student": "fas fa-user-graduate",
        "core.Teacher": "fas fa-chalkboard-teacher",
        "core.ParentPortal": "fas fa-user-friends",
        "core.Attendance": "fas fa-calendar-check",
        "core.Grade": "fas fa-star",
        "core.Payment": "fas fa-file-invoice-dollar",
        "core.Schedule": "fas fa-clock",
        "core.Subject": "fas fa-book",
        "core.Group": "fas fa-layer-group",
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-circle",
    "changeform_format": "horizontal_tabs",
    
    # Қўшимча тартиблар
    "order_with_respect_to": ["core.Student", "core.Teacher", "core.Subject", "core.Exam", "core.Grade"],
}

JAZZMIN_UI_TWEAKS = {
    "navbar": "navbar-dark navbar-teal",
    "theme": "flatly",
    "sidebar": "sidebar-dark-teal",
    "accent": "accent-teal",
    "navbar_fixed": True,
    "sidebar_fixed": True,
    "footer_fixed": False,
    "button_classes": {
        "primary": "btn-teal",
        "secondary": "btn-outline-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}