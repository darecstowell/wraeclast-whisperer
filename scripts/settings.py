import os

DATABASE_URL: str = os.environ.get("DATABASE_URL", "postgresql://root:root@localhost:5432/postgres")
GAME_DATA_EMBEDDING_MODEL: str = os.environ.get("GAME_DATA_EMBEDDING_MODEL", "text-embedding-ada-002")
GAME_DATA_VECTOR_DIM: int = int(os.environ.get("GAME_DATA_VECTOR_DIM", 1536))
