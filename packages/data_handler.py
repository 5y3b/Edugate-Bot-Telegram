import requests
from lxml import html

from os.path import exists, join
from typing import Optional
from os import makedirs
from enum import Enum
from time import time
from ujson import dumps

from .logger import Logger


class SUBJECT(Enum):
    """ Enums for subjects info """
    ID = '76'
    NAME = '78'
    TIME = '82'
    CLASS = '84'
    SECTION = '86'
    STATUS = '88'
    TEACHER = '90'

# stores info and its methods
class Subjects:
    """ Stores the subjects as a dictionary in list """
    def __init__(self):
        self.list = {}
        """This have IDs as keys and their values is
            a dictionary with SECTION_NUMBER as keys and values is
            another dictionary with keys in ['name', 'time', 'class', 'status', 'teacher']
            and each one value is the data about that section
            """
        self.list_last_updated = None
        
    
    def get_all_sections_info(self, ID: str) -> Optional[str]:
        """Gets the sections of an ID and return the info

            - ID: An id that contains 6 digits

            - Returns a `string` or `None` if ID is not found
            ### String example
            >>> 'NAME\\n\\n'
            >>> 'SECTION1, STATUS, CLASS\\n'
            >>> 'TIME, TEACHER\\n\\n'
            >>> 'SECTION2, STATUS, CLASS\\n'
            >>> 'TIME, TEACHER\\n\\n'
            ~"""
        ID = str(ID)
        if ID not in self.list:
            return None
        info: str = ''
        first_section_data = next(iter(self.list[ID].values()), None)
        if first_section_data:
            info += f"{first_section_data['name']}\n\n"
        for section, data in self.list[ID].items():
            info += f"{section:>2}, {data['status']:<6}, {data['class']}\n{data['time']}, {data['teacher']}\n\n"
        return info
        
    def get_section_info(self, ID: str, SECTION: str) -> Optional[str]:
        """Gets the entered SECTION of the entered ID 
            and return the info

            - ID: An id that contains 6 digits
            - SECTION: An int that represents the class number

            - Returns a `string` or `None` if ID or SECTION is not found
            ### String example
            >>> 'NAME\\n'
            >>> 'STATUS, CLASS, TIME, TEACHER\\n'
        
            ~"""
        ID = str(ID)
        SECTION = str(SECTION)
        if ID not in self.list or SECTION not in self.list[ID]:
           return None
        data = self.list[ID][SECTION]
        return (f"{data['name']}\n"
                f"{data['status']:<6}, {data['class']}, {data['time']}, {data['teacher']}\n")

    def search_by_name(self, subject_name: str ='') -> dict:
        """
            searches for an occurnce of subject_name in
            the subject name if found saves it to a dict
            with the ID of the subject as key and the 
            name of the subject as value
            
            - subject_name: the subject name you want to 
              know its ID {optional}

            -- returns a {'ID' : 'POSSIBLE_NAME_MATCH'} 
               dict of possible name matches

            -- returns list of all IDs and NAMEs if no 
               parameter is given
        """

        found_list = {}
        for ID, value in self.list.items():
            name : str = ''
            for _section, data in value.items():
                name = data['name']
                break

            if name.find(subject_name) != -1:
                found_list[ID] = name
        return found_list

    def save_to_file(self, file_name: str='subjects_list', directory: str='data/') -> int:
        """Saves the `self.list` dictionary to a JSON file.

            - file_name: A name for your file, defaults to 'subjects_list'.
            - directory: The directory where your file will be saved, defaults to 'data/'.

            -- format always is .json
            -- returns positive on success:
                1: Successful save.
            -- returns negative on failure:
                -1: No subjects to save.
                -2: Permission denied.
                -3: I/O error occurred.
                -4: Unexpected error occurred."""
        if not self.list:
            print("No subjects to save")
            return -1

        from os import makedirs
        from os.path import exists, join
        try:
            if not exists(directory):
                makedirs(directory)
            
            file_path = join(directory, file_name)

            from json import dump
            with open(f'{file_path}.json', 'w', encoding='utf-8') as file:
                dump(self.list, file, indent=4, ensure_ascii=False)
            return 1
        except PermissionError:
            print("Permission denied: Unable to write to the file or directory.")
            return -2
        except IOError as e:
            print(f"An I/O error occurred: {e}")
            return -3
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return -4

    def print_to_console(self) -> None:
        """
            This method prints self.list into console:

            - Not recommended because there is alot of text to print
        """
        print(dumps(self.list, indent=4, ensure_ascii=False))

    def time(self) -> float:
        """Returns the time in seconds since the last update"""
        return (time() - self.list_last_updated)        

    def __repr__(self):
        return f"SubjectsList(len={len(self.list)})"
    
    def __str__(self):
        return f"SubjectsList(len={len(self.list)})"
    

# handles data gathering
class DataSession:
    """ 
        Session class that will handle the session and gather the information needed
    """
    def __init__(self):
        self.__response = None
        self.__logger = Logger(self.__class__.__name__)
        self.__session = requests.Session()
        self.__url = 'https://edugate.jadara.edu.jo/timetable'
        
    def run(self) -> Optional[Subjects]:
        """Handles all of the logic of sending the get 
            request then handles neccessary data and 
            handles the post request then handles the
            parsing of data



            - On success returns Subjects() object and None on fail"""
        self.__payload = self._create_data(self._get_viewstate())
        return self._update()

    def close(self) -> None:
        """Closes the session"""
        self.__session.close()
        
    def _update(self) -> Optional[Subjects]:
        """Updates the data the session and returns Subjects() object"""
        is_success = self._send_post()
        if not is_success:
            return None
        subjects = self._scrape_data()
        subjects.list_last_updated = time()
        return subjects
        
    def _get_viewstate(self) -> str:
        """
            Gets viewstate since it is dynamically 
            changed for every session

            - This makes sure to get it in the current page 
            - Returns viewstate value
        """
        response = self.__session.get(self.__url)
        viewstate = html.fromstring(response.content).xpath("//input[@name='javax.faces.ViewState']/@value")[0]
        return viewstate
    
    def _create_data(self, viewstate: str) -> dict:
        """Creates the required data for the post requests and returns them as a tuple
            - `viewstate`: the viewstate value from the _get_viewstate method
            - `returns`: payload as a dict"""
        payload = {
            'javax.faces.partial.ajax': 'true', # essential to not receieve all of page contents
            'javax.faces.source': 'serviceContents:scheduleDtl::j_idt68',
            'javax.faces.partial.execute': '@all',
            'javax.faces.partial.render': 'serviceContents:scheduleDtl serviceContents:msgs',
            'serviceContents:scheduleDtl:j_idt68': 'serviceContents:scheduleDtl:j_idt68',
            'serviceContents': 'serviceContents',
            'serviceContents:scheduleDtl_pagination': 'true',
            'serviceContents:scheduleDtl_first': '0',
            'serviceContents:scheduleDtl_rows': '4000',
            'serviceContents:scheduleDtl_rppDD': '4000',
            # 'serviceContents:scheduleDtl_skipChildren': 'true', # not needed
            'serviceContents:scheduleDtl_encodeFeature': 'true',
            'javax.faces.ViewState': viewstate
        }
        return payload
    
    def _send_post(self) -> bool:
        """Sends post request to get the data for this session
            and saves it to self.__response

            Creates a response for the post
            - self.__response

            - Returns True on success and False on fail"""
        self.__response = self.__session.post(self.__url, data=self.__payload)
        
        if len(self.__response.text) < 1000000: 
            self.__logger.error('Data retrieval failed. status={}, len(response)={}, time={}'.format(
                self.__response.status_code, 
                len(self.__response.text),
                self.__response.elapsed
            ))
            return False
        self.__logger.info('Data retrieval success. status={}, len(response)={}, time={}'.format(
                self.__response.status_code, 
                len(self.__response.text),
                self.__response.elapsed
            ))
        return True
    
    def _scrape_data(self) -> Subjects:
        """
            Scrapes the data from the response of the post
            contained in self.__response using lxml

            - MUST NOT TRIGGER IF _send_post IS FAIL

            - Returns Subjects() object
        """
        all_labels = html.fromstring(self.__response.content).xpath("//label")
        
        subjects = Subjects()
        """
            dictionary format subjects.list['SUBJECT_ID']['SECTION']['name', 'time', 'class', 'status', 'teacher']
            SUBJECT_ID = str(NUMBER), whose length is 6
            SECTION = str(NUMBER)
        """

        temp_info = {}
        current_id = None
        current_section = None
        
        for label in all_labels:
            # getting the identifier and info ready 
            identifier: str = label.get('id')[28:]
            identifier = identifier[0:identifier.find(':')] + identifier[-2:]
            """
                identifier format : f'{int}{TWO_NUMBERS}'
                TWO_NUMBERS = ['76','78','82','84','86','88','90']
            """
            info = label.text_content().strip()
            """
                info indicates a specific value for each number in 
                TWO_NUMBERS all belonging to the same int number
            """
            
            # logic of inserting data into the dictionary called subjects_list
            if identifier[-2:] == SUBJECT.ID.value:
                if current_section:
                    subjects.list[current_id][current_section] = temp_info
                    temp_info = {} 
                current_id = info
                if current_id not in subjects.list:
                    subjects.list[current_id] = {}
            elif identifier[-2:] == SUBJECT.SECTION.value:
                current_section = info
                if current_id:
                    subjects.list[current_id][current_section] = temp_info
            else:  
                if identifier[-2:] == SUBJECT.NAME.value:
                    temp_info['name'] = info
                elif identifier[-2:] == SUBJECT.TIME.value:
                    temp_info['time'] = info
                elif identifier[-2:] == SUBJECT.CLASS.value:
                    temp_info['class'] = info
                elif identifier[-2:] == SUBJECT.STATUS.value:
                    temp_info['status'] = info
                elif identifier[-2:] == SUBJECT.TEACHER.value:
                    temp_info['teacher'] = info
        if current_id and current_section:
            subjects.list[current_id][current_section] = temp_info
        subjects.last_update = time()
        return subjects



__all__ = ['dataSession', 'Subjects']