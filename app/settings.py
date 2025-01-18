import os
from typing import Optional

OPENAI_API_KEY: Optional[str] = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL: str = os.environ.get("OPENAI_MODEL", "gpt-4o")
DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://root:root@localhost:5432/postgres")
DEPLOYMENT: str = os.environ.get("DEPLOYMENT", "local")
