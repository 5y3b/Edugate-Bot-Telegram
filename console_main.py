from packages import data_handler

class console_main:
    def __init__(self):
        self.data_handler = data_handler.DataSession()

    def start_session(self):
        if (response := self.data_handler.run()):
            response.save_to_file('subjects_list')
            
            # print(response.search_by_name('برمجة'))
            # IdName_list = response.search_by_name()
            # with open('IdName_list.txt', 'wb') as file:
            #     for Id, Name in IdName_list.items():
            #         file.write(f'{Id}:{Name}\n'.encode('utf-8'))

            Search_list = response.get_all_sections_info(508365)
            print(Search_list)
            # with open('Search_list.txt', 'wb') as file:
            #     for Id, Name in Search_list.items():
            #         file.write(f'{Id}:{Name}\n'.encode('utf-8'))


            



if __name__ == '__main__':
    main = console_main()
    main.start_session()
    