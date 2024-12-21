import os

from dotenv import load_dotenv

load_dotenv()

NAME = os.getenv("WW_NAME", "Wraeclast Whisperer")
MODEL = os.getenv("WW_MODEL", "gpt-4o-mini")
CALLBACK_USER = os.getenv("WW_CALLBACK_USER", "Assistant")
TEMPLATE_TITLE = os.getenv("WW_TEMPLATE_TITLE", "Wraeclast Whjisperer")
PORT = int(os.getenv("WW_PORT", "5007"))
HOST = os.getenv("WW_HOST", "0.0.0.0")
WEBSOCKET_ORIGINS = os.getenv("WW_WEBSOCKET_ORIGINS", "localhost:5007").split(",")
SHOW_PANEL = os.getenv("WW_SHOW_PANEL", "True").lower() == "true"
