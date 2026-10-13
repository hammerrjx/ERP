import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv("ERP_SECRET_KEY", "dev-only-change-me")
DEBUG = os.getenv("ERP_DEBUG", "1") == "1"
ERP_DELIVERY_POST_STOCK = os.getenv("ERP_DELIVERY_POST_STOCK", "0") == "1"
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "backend",
    "backend.importing",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]
ROOT_URLCONF = "erp_backend.urls"
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]
WSGI_APPLICATION = "erp_backend.wsgi.application"
DATABASES = {"default": {
    "ENGINE": "django.db.backends.sqlite3", "NAME": os.getenv("ERP_SQLITE_PATH", BASE_DIR / "db.sqlite3"),
    "OPTIONS": {"transaction_mode": "IMMEDIATE", "timeout": 20},
}}
if os.getenv("ERP_DB_ENGINE") == "mssql":
    DATABASES["default"] = {
        "ENGINE": "mssql", "NAME": os.environ["ERP_DB_NAME"],
        "HOST": os.getenv("ERP_DB_HOST", "localhost"),
        "USER": os.getenv("ERP_DB_USER", ""), "PASSWORD": os.getenv("ERP_DB_PASSWORD", ""),
        "OPTIONS": {"driver": os.getenv("ERP_DB_DRIVER", "ODBC Driver 18 for SQL Server"),
                    "extra_params": os.getenv("ERP_DB_EXTRA_PARAMS", "TrustServerCertificate=yes")},
    }
elif os.getenv("ERP_DB_NAME"):
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ["ERP_DB_NAME"],
        "USER": os.getenv("ERP_DB_USER", "postgres"),
        "PASSWORD": os.getenv("ERP_DB_PASSWORD", ""),
        "HOST": os.getenv("ERP_DB_HOST", "127.0.0.1"),
        "PORT": os.getenv("ERP_DB_PORT", "5432"),
    }
AUTH_PASSWORD_VALIDATORS = []
LANGUAGE_CODE = "zh-hans"
TIME_ZONE = "Asia/Shanghai"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
CORS_ALLOWED_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["rest_framework.authentication.TokenAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}

# Enable only in a complete test ledger until formal inventory cutover is approved.
ERP_NO_ORDER_RETURN_POST_STOCK = os.getenv("ERP_NO_ORDER_RETURN_POST_STOCK", "0") == "1"

# Enable only after the local trade stock/open-document baseline is accepted.
ERP_TRADE_MRP_GENERATION_ENABLED = os.getenv("ERP_TRADE_MRP_GENERATION_ENABLED", "0") == "1"
