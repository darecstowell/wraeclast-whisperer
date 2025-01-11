import argparse
import asyncio

import bcrypt
from chainlit.data.chainlit_data_layer import ChainlitDataLayer
from chainlit.user import User

from app.settings import DATABASE_URL

parser = argparse.ArgumentParser()
parser.add_argument("--username", help="Username")
parser.add_argument("--password", help="Password")
args = parser.parse_args()


def create_user(username: str, password: str):
    """
    Create a user with the given username and password
    NOTE: This will override the existing user if the username already exists
    """
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    metadata = {"password": hashed_password.decode("utf-8")}
    user = User(identifier=username, metadata=metadata)
    asyncio.run(ChainlitDataLayer(DATABASE_URL).create_user(user))


create_user(args.username, args.password)
