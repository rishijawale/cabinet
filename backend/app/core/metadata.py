from app.core.config import BACKEND_DIR
from app.models import *  # noqa: F401,F403 - register all models on the metadata

config_path = BACKEND_DIR / "alembic.ini"
