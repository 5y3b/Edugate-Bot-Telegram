# if M exists means Markdown is used
# if F is used that means .format is needed

COMMANDS_LIST = (
    f'You can use the following commands:\n'
    f'/help - Get a list of available commands and their descriptions.\n\n'

    f'/search <NAME> - Search for a subject by name or keyword.\n\n'

    f'/get <ID> - Gets all the sections info about a subject.\n'
    f'/get <ID> <SECTION> - Gets the specified section only.\n\n'

    f'/fav - Shows the favorite editor, as you may show, add, delete, clear.\n\n'

    f'/suggest - Suggest a feature to be added.\n')


SEARCH_ERROR_1 = (
    'Please enter a subject name to search\n\n'
    'Example:\n/search برمجة or /search مهارات\n')
SEARCH_ERROR_2 = (
    'Subject name have to be more than 2 letters\n\n'
    'Example:\n/search برمجة or /search مهارات -✔\n'
    '/search ب or /search مه -✖\n')
SEARCH_ERROR_3 = (
    'Results are too long, please try to search with a more specific subject name.\n\n'
    'Example:\n/search برمجة instead of /search برم\n')
SEARCH_LOG_1F = (
    'func={}, searched_for={}')

GET_ERROR_1M = (
    'Please enter subject ID to get its info\n'
    '/get ID SECTION\n\n'
    'ID is a 6 digit number!\n'
    'SECTION is 2 digits at most! [Optional]\n\n'
    'Example:\n'
    '/get `185103` or /get `183109` ✔\n'
    '/get `185103` `1` or /get `183109` `5` ✔✔\n')
GET_ERROR_2FM = (
    '`{}` must be a number with 6 digits 😭!\n\n'
    'Example:\n'
    '/get `185103` or /get `183109` ✔\n')
GET_ERROR_3FM = (
    '`{}` must be a number 🤓!\n\n'
    'Example:\n'
    '/get `185103` `1` or /get `183109` `5` ✔✔\n')
GET_WAIT_1F = (
    'Fetching all {} data...\n'
    'Hold your tea! 😀🔥')
GET_WAIT_2F = (
    'Fetching {} {} data...\n'
    'Hold your tea! 😀🔥')
GET_RESULT_1FM = (
    "'{}' doesn't match courses 😔!\n")
GET_RESULT_2FM = (
    "'{}' doesn't match any course with '{}' as section 😔!\n")
GET_LOG_1F = (
    'func={}, id={}, section={}')

FAV_ERROR_1M = (
    'How to use the /fav\n'
    '`/fav show` - Shows your favorite list\n'
    '`/fav add` ID SECTION - Adds the SECTION of an ID to your favorite list\n'
    '`/fav delete` ID SECTION - Deletes the SECTION of an ID from your favorite list\n'
    '`/fav clear` - Clears all of the favorites list ~CAREFUL\n\n'

    'ID is a 6 digit number!\n'
    'SECTION is at most 2 digit number\n\n'

    'Example:\n'
    '`/fav show`\n'
    '`/fav add` `185103` `1` or /fav add 183109 4\n'
    '`/fav delete` `185103` `1` or /fav delete 183109 4\n'
    '`/fav clear`\n')
FAV_ERROR_2F = (
    '{} argument error!\n\n'

    'Correct arguments are:\n'
    'show, add, delete\n\n'

    'call /fav for detailed explanation\n')
FAV_ERROR_3FM = (
    '`{}` must be number with 6 digits 😭!\n\n'
    'Example:\n'
    '`/fav add` `185103` `1` or `/fav delete` `185103` `1` ✔✔\n')
FAV_ERROR_4FM = (
    '`{}` must be a number with at most 2 digits 🤓!\n\n'
    'Example:\n'
    '`/fav add` `185103` `1` or `/fav delete` `185103` `1` ✔✔\n')
FAV_WAIT_1 = (
    'Preforming hard calculations!\n'
    'Please wait 🙄🌹')
FAV_LOG_1F = (
    'func={}, type={}, id={}, section={}')


