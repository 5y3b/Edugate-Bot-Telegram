import customtkinter as ctk
import tkinter as tk


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram App")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        self.root.configure(bg="#2f343a")
        self.root.iconbitmap("gui/curlogo.ico")
        
        
        self.__create_elements()
        self.__place_elements()
        
        
        
        
        self.root.mainloop()
    
    def __create_elements(self) -> None:
        self.__activation_frame = ActivationFrame(self.root)
        
        
                
    
    def __place_elements(self):
        self.__activation_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        pass
        
class ActivationFrame(ctk.CTkFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.__master = master
        self.__create_elements()
        self.__place_elements()
        
    def __create_elements(self):
        self.__start_label = \
            ctk.CTkLabel(self, text="Start", font=("Arial", 24))
        pass
    
    def __place_elements(self):
        self.__start_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        pass
        


root = ctk.CTk()
app = App(root)