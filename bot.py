from load_dotenv import load_dotenv
from os import getenv

from packages.telegram_bot import TeleSession
from packages import paths

load_dotenv(paths.env)
TELE_TOKEN = getenv('TELE_TOKEN')




a = TeleSession(TELE_TOKEN)
try:      
    a.start()
except KeyboardInterrupt as e:
    print(f"Stopping bot...")
    a.stop()
    