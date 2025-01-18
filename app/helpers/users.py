import bcrypt
from chainlit.data.chainlit_data_layer import ChainlitDataLayer
from chainlit.user import User

from app.settings import DATABASE_URL


async def get_or_create_user(username: str, password: str) -> User | None:
    """
    Get or create a user with the given username and password
    """
    existing_user = await ChainlitDataLayer(DATABASE_URL).get_user(identifier=username)
    if existing_user:
        return existing_user
    else:
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        metadata = {"password": hashed_password.decode("utf-8")}
        user = User(identifier=username, metadata=metadata)
        return await ChainlitDataLayer(DATABASE_URL).create_user(user)
