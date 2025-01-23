import os

DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://root:root@localhost:5432/postgres")
