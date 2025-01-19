from load_dotenv import load_dotenv
from time import sleep
from os import getenv

from packages.telegram_bot import TeleSession
from packages import paths

load_dotenv(paths.env)
TELE_TOKEN = getenv('TELE_TOKEN')




a = TeleSession(TELE_TOKEN)


a.start()
try:
    input("Enter anything to stop\n")
    a.stop()
except KeyboardInterrupt as e:
    print("Keyboard Interrupt, stopping")
    a.stop()
    
