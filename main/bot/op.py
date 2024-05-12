from discord import Intents
from pathlib import Path

from .client import IA24Client

base_dir = Path(__file__).resolve().parent.parent.parent
bot_token = (base_dir / "bot-token.secret.txt").read_text()

# Bot setup
intents = Intents.all()
client = IA24Client(intents=intents)

async def start_bot():
    await client.start(token=bot_token)