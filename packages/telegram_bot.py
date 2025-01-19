import telebot
from os.path import exists
import ujson
from time import sleep
import threading

from .data_handler import DataSession
from .logger import Logger
from . import paths
from . import MESSAGES


class TeleSession(telebot.TeleBot):
    """A class to represent a Telegram bot session.

        This class extends the `telebot.TeleBot` class and provides additional functionalities
        for handling user sessions, logging, and managing favorite subjects.

        Attributes:
        -----------
            __active_users : dict
                A dictionary to keep track of active users.
            __errorLogger : Logger
                A logger instance for logging errors.
            __infoLogger : Logger
                A logger instance for logging informational messages.
            __userLogger : Logger
                A logger instance for logging user activities.
            is_polling : bool
                A flag to indicate if the bot is currently polling.
            polling_thread : threading.Thread
                A thread for polling the bot.
            __favorites : dict
                A dictionary to store user favorites.

        Methods:
        --------
            start():
                Starts the telegram session and begins listening for messages.
            stop():
                Stops the telegram session and clears active users.
            __START(message: telebot.types.Message):
                Handles the /start command.
            __HELP(message: telebot.types.Message):
                Handles the /help command.
            __SEARCH(message: telebot.types.Message) -> bool:
                Handles the /search command.
            __GET(message: telebot.types.Message) -> int:
                Handles the /get command.
            __FAV(message: telebot.types.Message) -> bool:
                Handles the /fav command.
            __SUGGEST(message: telebot.types.Message):
                Handles the /suggest command.
            __FavoriteHandler(user_id: str, handleType: str, subject_id: str, section_number: str):
                Manages favorite commands.
            __isUserActive(message: telebot.types.Message) -> bool:
                Checks if a user is active.
            __Update(force_update: bool=False):
                Updates the subjects data.
            __runPolling():
                Runs the polling thread.
            __LogUser(message: telebot.types.Message, log_message: str=None) -> None:
                Logs user information.
            __Exit(message: telebot.types.Message, log_user: bool=False, log_message: str=None):
                Removes user from active list and logs if needed."""
    
    def __init__(self, token: str, *args, **kwargs):
        if token == None or len(token) < 40:
            raise ValueError('Token is empty, please set TELE_TOKEN correctly, '
                             'please go to /data/telegram_bot.env and fix it.')
        super().__init__(token, *args, **kwargs)
        
        self.__active_users = {}
        self.__errorLogger = Logger('ErroLogger', 'errorlogs.log', paths.infologs_folder)
        self.__infoLogger = Logger(self.__class__.__name__, logs_folder=paths.infologs_folder)
        self.__userLogger = Logger('userLogger', 'userlogs.log', paths.userlogs_folder)

        self.is_polling = True
        self.__stop_event = threading.Event()
        self.polling_thread = None

        # loading favorites / path will always exist
        with open(paths.fav, 'r', encoding='utf-8') as file:
            self.__favorites: dict = ujson.load(file)
        
        self.__session = DataSession()
        self.__subjects = self.__session.run()
        
  
    def start(self):
        """Starts the telegram session and starts listening for messages"""
        self.is_polling = True
        self.__stop_event.clear()
        
        self.message_handler(commands=['start'])(self.__START)
        self.message_handler(commands=['help'])(self.__HELP)
        self.message_handler(commands=['search'])(self.__SEARCH)
        self.message_handler(commands=['get'])(self.__GET)
        self.message_handler(commands=['fav'])(self.__FAV) # TODO
        self.message_handler(commands=['suggest'])(self.__SUGGEST)

        # TODO Threading issue exists, cant ctrl+c the program
        if self.polling_thread is None or not self.polling_thread.is_alive():
            self.polling_thread = threading.Thread(target=self.__runPolling)
            self.polling_thread.start()
            
               
    def stop(self):
        """Stops the telegram session and stops listening for messages"""
        self.is_polling = False
        self.__stop_event.set()
        self.stop_polling()
        self.__active_users.clear()
        self.__session.close()
        
        if self.polling_thread:
            self.polling_thread.join()
            self.polling_thread = None

    def __START(self, message: telebot.types.Message) -> None:
        """This is the default function for the /start command"""
        hello_message = f'Hello {message.from_user.first_name}!'

        self.send_message(
            message.chat.id,
            hello_message
        )
        self.send_message(
            message.chat.id,
            MESSAGES.COMMANDS_LIST
        )

        self.__LogUser(message)

    def __HELP(self, message: telebot.types.Message) -> None:
        self.send_message(message.chat.id, MESSAGES.COMMANDS_LIST)

    def __SEARCH(self, message: telebot.types.Message) -> bool:
        if self.__isUserActive(message):
            return False 
        
        text_list = message.text.split()

        if len(text_list) == 1:
            self.send_message(message.chat.id, MESSAGES.SEARCH_ERROR_1)
            self.__Exit(message)
            return False

        subject_name = str(text_list[1])
        if len(subject_name) <= 2:
            self.send_message(
                message.chat.id, MESSAGES.SEARCH_ERROR_2
            )
            self.__Exit(message)
            return False
        searching_message = self.send_message(message.chat.id, 'Searching...')
        results = self.__subjects.search_by_name(subject_name)
        result_text = "ID: Name\n"
        for Id, Name in results.items():
            result_text += f"`{Id}`: {Name}\n"


        if len(result_text) > 4000:
            self.send_message(message.chat.id, MESSAGES.SEARCH_ERROR_3)
            self.__Exit(message)
            return False
        
        if not results:
            self.edit_message_text(f'No match found for `{subject_name}`! 💀', message.chat.id, searching_message.id, parse_mode="Markdown")
        else:
            self.edit_message_text(result_text, message.chat.id, searching_message.id, parse_mode="Markdown")
        self.__Exit(message, True, MESSAGES.SEARCH_LOG_1F.format(self.__SEARCH.__name__, '-'.join(text_list[1:])))
        return True
    
    def __GET(self, message: telebot.types.Message) -> int:
        if self.__isUserActive(message):
            return False
        text = message.text.split()
        if len(text) == 1:
            self.send_message(message.chat.id, MESSAGES.GET_ERROR_1M, parse_mode='Markdown')
            self.__Exit(message)
            return False
        subject_id = str(text[1])
        if len(subject_id) != 6 or not subject_id.isnumeric():
            self.reply_to(message, MESSAGES.GET_ERROR_2FM.format(subject_id), parse_mode='Markdown')
            self.__Exit(message)
            return False
        subject_section = str(text[2]) if len(text) > 2 else None
        if subject_section and not subject_section.isnumeric():
            self.reply_to(message, MESSAGES.GET_ERROR_3FM.format(subject_section), parse_mode='Markdown')
            self.__Exit(message)
            return False

        result_text = ''
        getting_message = None
        if subject_section is None:
            ## ony ID
            getting_message = self.send_message(message.chat.id, MESSAGES.GET_WAIT_1F.format(subject_id))
            self.__Update()
            result_text = self.__subjects.get_all_sections_info(subject_id) or MESSAGES.GET_RESULT_1FM.format(subject_id)
        else:
            ## ID and SECTION
            getting_message = self.send_message(message.chat.id, MESSAGES.GET_WAIT_2F.format(subject_id, subject_section))
            self.__Update()
            result_text = self.__subjects.get_section_info(subject_id, subject_section) or MESSAGES.GET_RESULT_2FM.format(subject_id, subject_section)
        
        self.edit_message_text(result_text, message.chat.id, getting_message.id, parse_mode='Markdown')
        self.__Exit(message, True, MESSAGES.GET_LOG_1F.format(self.__GET.__name__, subject_id, subject_section or 'None'))
        return True
        
    def __FAV(self, message: telebot.types.Message) -> bool:
        if self.__isUserActive(message):
            return 0

        fav_commands = ['show', 'add', 'delete', 'clear']
        noArgCommands = ['show', 'clear']
        text = message.text.split()

        error_message = None

        if len(text) == 1:
            # check if only one word is provided
            error_message = MESSAGES.FAV_ERROR_1M
        elif not text[1] in fav_commands:
            # check if second word is not in fav_commands
            error_message = MESSAGES.FAV_ERROR_2F.format(text[1])
        elif (len(text) < 3 or len(text[2]) != 6 or not text[2].isnumeric()) and text[1] not in noArgCommands:
            # check the subject id argument
            error_message = MESSAGES.FAV_ERROR_3FM.format(text[2] if len(text) > 2 else 'ID')
        elif (len(text) < 4 or len(text[3]) > 2 or not text[3].isnumeric()) and text[1] not in noArgCommands:
            # check the section number argument
            error_message = MESSAGES.FAV_ERROR_4FM.format(text[3] if len(text) > 3 else 'SECTION')

        # if there is an error, send the message and exit
        if error_message:
            self.send_message(message.chat.id, error_message, parse_mode='Markdown')
            self.__Exit(message)
            return False

        wait_message = self.send_message(message.chat.id, MESSAGES.FAV_WAIT_1)
        handleType = text[1]
        subject_id = None
        section_number = None
        if handleType not in noArgCommands:
            subject_id = text[2]
            section_number = text[3]
        
        
        result = self.__FavoriteHandler(message.from_user.id, handleType, subject_id, section_number)
        
        self.edit_message_text(result, message.chat.id, wait_message.id)
        self.__Exit(message, True, MESSAGES.FAV_LOG_1F.format(self.__FAV.__name__, handleType, subject_id, section_number))
        return True

    
    def __SUGGEST(self, message: telebot.types.Message):
        # TODO
        pass

    def __FavoriteHandler(self, user_id: str, handleType: str, subject_id: str, section_number: str):
        """Handles the three cases of the favorite commands
            :param user_id: The id of the user to handle
            :param handleType: The type of the favorite command [`show`, `add`, `delete`, `clear`]
            :param subject_id: The id of the subject
            :param section_number: The number of the section
            
            ~"""
        # 0 -> a response text is not ready
        # 1 -> a response text is ready
        # 2 ->
        status = 0
        response_text = ''
        if handleType == 'add':
            if section_number not in self.__favorites.get(user_id, {}).get(subject_id, {}):
                self.__favorites.setdefault(user_id, {}).setdefault(subject_id, []).append(section_number)
                response_text = f'{subject_id} {section_number} added successfully!\n'
            else:
                response_text = f'{subject_id} {section_number} already in favorites!\n'
            status = 1
            # update favorite file
            with open(paths.fav, 'w', encoding='utf-8') as file:
                ujson.dump(self.__favorites, file, indent=4)
                
        elif handleType == 'show':
            self.__Update()
            for ID, SECTIONS in self.__favorites.get(user_id, {}).items():
                for section in SECTIONS:
                    response_text += f'{section} | {ID} | {self.__subjects.get_section_info(ID, section)}'
            if response_text == '':
                response_text = 'No favorites to show 🤡!'
            status = 1
        elif handleType == 'delete':
            if subject_id not in self.__favorites.get(user_id, {}):
                response_text = f'{subject_id} not found in favorites!\n'
            elif section_number in self.__favorites.get(user_id, {}).get(subject_id, []):
                self.__favorites[user_id][subject_id].remove(section_number)
                response_text = f'{subject_id} {section_number} deleted successfully!\n'

                # Remove subject ID if no more sections are left
                if not self.__favorites.get(user_id, {})[subject_id]:
                    del self.__favorites.get(user_id, {})[subject_id]

                # Update favorite file
                with open(paths.fav, 'w', encoding='utf-8') as file:
                    ujson.dump(self.__favorites, file, indent=4)
            else:
                response_text = f'{subject_id} {section_number} not found in favorites!\n'
            status = 1
            
        elif handleType == 'clear':
            if self.__favorites.pop(user_id, None):
                response_text = 'Favorites cleared successfully!\n'
            else:
                response_text = 'No favorites to clear!'
                
            status = 1
            with open(paths.fav, 'w', encoding='utf-8') as file:
                ujson.dump(self.__favorites, file, indent=4)
        else:
            status = 2
        return response_text if status == 1 else 'ERROR'

    def __isUserActive(self, message: telebot.types.Message) -> bool:
        """
            Checks if user is active
            - if active sends a message and returns true
            - if not active returns false and appends user to active users
        """
        chat_id = str(message.chat.id)
        if chat_id in self.__active_users:
            self.send_message(chat_id, 'Wait for your request! ♥')
            return True
        else: 
            self.__active_users[chat_id] = None
            return False

    def __Update(self, force_update: bool=False):
        """An updater for the status of subjects updater 
            only runs when called and minimum time between
            updates is 20 seconds
            
            - updates self.__subjects
            - you can force update it by setting the 
              parameter force_update to True"""
        if force_update or self.__subjects.time() > 20:
            self.__subjects = self.__session.run()
            
    def __runPolling(self):
        """
            This method is called when creating a thread 
            to start polling the bot
        """
        while not self.__stop_event.is_set():
            try:
                self.polling(none_stop=True, long_polling_timeout=0)
            except Exception as e:
                self.__errorLogger.exception(f'Func={self.__runPolling.__name__}, Error: {e}')
                sleep(10)

    def __LogUser(self, message: telebot.types.Message, log_message: str=None) -> None:
        """Logs user to the userlog file and creates a user-only log file
            :param message: The message object of the user
            :param log_message: The message to be logged
                
            ~"""
        user_info = message.from_user
        
        user_id = user_info.id
        first_name = user_info.first_name
        last_name = user_info.last_name
        username = user_info.username
        language_code = user_info.language_code
        
        user_details = (
            f"User ID: {user_id}\n"
            f"First Name: {first_name}\n"
            f"Last Name: {last_name}\n"
            f"Username: @{username}\n"
            f"Language: {language_code}\n")
        log_user = (
            f'{user_id:<12} '
            f'{first_name + last_name:<12} '
            f'{str(username):<8} '
            f'{language_code} -- '
            f'{log_message or 'None'}')
        self.__userLogger.info(log_user)
        
        user_path = f'{paths.userlogs_folder}/{user_id}_{first_name}.txt'
        if not exists(user_path):
            with open(user_path, 'w', encoding='utf-8') as file:
                file.write(user_details)
            

    def __Exit(self, message: telebot.types.Message, log_user: bool=False, log_message: str=None):
        """This function removes user from active list when called and logs if needed
            :param message: the message of the user
            :param log_user: Whether to log the user or not
            :param log_message: The message to log

            ~"""
        self.__active_users.pop(str(message.from_user.id), False)
        if log_user:
            self.__LogUser(message, log_message)
        
        
