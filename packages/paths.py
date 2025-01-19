from os import makedirs
from os.path import exists



env = 'data/telegram_bot.env'
fav = 'data/favorites.json'
infologs_folder = 'data/logs'
userlogs_folder = 'data/logs/user_logs'

# creating dirs if not exist
makedirs(infologs_folder, exist_ok=True)
makedirs(userlogs_folder, exist_ok=True)

if not exists(env):
    with open(env, 'w') as file:
        file.write('TELE_TOKEN=\n')
if not exists(fav):
    with open(fav, 'w') as file:
        file.write('{}')