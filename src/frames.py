# 3rd party imports
import tkinter as tk
from tkinter import filedialog as fd 
from tkinter import ttk
import os
from enum import Enum

# Custom files import
from scraper import *

class Buttons_Frame(tk.Frame):
    def __init__(self, master, button_names: list = None, button_actions: list = None) -> None:
        super().__init__(master, bg="grey")

        self.buttons = []        
        if(button_names != None and button_actions != None):
            assert len(button_names) == len(button_actions)

            for button_name, button_action in zip(button_names, button_actions):
               button = tk.Button(master=self, text=button_name, command=button_action)
               button.pack(pady=10, padx=10)
               self.buttons.append(button)

    def get_button_by_text(self, text):

        for button in self.buttons:
            if(button.cget("text") == text):
                return button

        return None
    


class About_Frame(tk.Frame):
    def __init__(self, master) -> None:
        super().__init__(master)

        about_text = "TODO: how to use program text"
        self.about_label = tk.Label(self, text=about_text)
        self.about_label.pack(padx=50, pady=50)
    


class Car_Choose_Frame(tk.Frame):

    # Should be also called after the constructor
    def refresh_offerings_data(self):
        self.available_models, self.brand_to_models = self.scraper.get_brands_and_models()

        self.brand_combobox.config(state="readonly")
        self.model_combobox.config(state="disabled")
        self.start_scrape_button.config(state="disabled")
        
        self.brand_combobox.config(values=self.available_models)
        self.model_combobox.config(values=[])

        self.brand_combobox.set(self.DEFAULT_COMBOBOX_TEXT) # Clearing the comboboxes selections
        self.model_combobox.set(self.DEFAULT_COMBOBOX_TEXT) # 


    def _chose_brand(self, event):
        selected_brand = event.widget.get()
        self.model_combobox.config(state="readonly", values=self.brand_to_models[selected_brand])
        self.model_combobox.set(self.DEFAULT_COMBOBOX_TEXT)

        self.start_scrape_button.config(state="disabled")

    def _chose_model(self, event):
        self.start_scrape_button.config(state="normal")

    def _change_state_to(self, state: str, text_color: str):
        self.state_label.config(text=state, fg=text_color)

    #TODO start scrapeing and save it into data/brand_model.csv
    def _start_scrape(self):
        brand = self.brand_combobox.get()
        model = self.model_combobox.get()
        save_name = os.getcwd() + "/data/" + brand + '_' + model.strip()

        self.scraper.scrape_brand_model(brand, model, save_name)

    def __init__(self, master) -> None:
        super().__init__(master)
 
        WIDGETS_PADDING_X = 5
        WIDGETS_PADDING_Y = 5 

        self.DEFAULT_COMBOBOX_TEXT = "Pick an option"
        

        #Firstly set widgets for model selection
        self.brand_label = tk.Label(self, text="Choose car brand")
        self.brand_label.pack(padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

        self.brand_combobox = ttk.Combobox(self, values=[], state="disabled")
        self.brand_combobox.set(self.DEFAULT_COMBOBOX_TEXT)
        self.brand_combobox.bind("<<ComboboxSelected>>", self._chose_brand)
        self.brand_combobox.pack(padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

        #Secondly set widgets for model selection
        self.model_label = tk.Label(self, text="Choose car model")
        self.model_label.pack(padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

        self.model_combobox = ttk.Combobox(self, state="disabled")
        self.model_combobox.set(self.DEFAULT_COMBOBOX_TEXT)
        self.model_combobox.bind("<<ComboboxSelected>>", self._chose_model)
        self.model_combobox.pack(padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)
        
        #Lastly set state widget label
        self.state_label = tk.Label(self, text="")
        #self.state_label.pack(padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)        
        
        self.refresh_button = tk.Button(self, text="Get/Refresh available \nbrands and models", command=self.refresh_offerings_data)
        self.refresh_button.pack(padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

        # Construct scraper
        self.scraper = AutobazarEuScraper()

        # TODO scraper button
        self.start_scrape_button = tk.Button(self, text="start scraping", command=self._start_scrape, state="disabled")
        self.start_scrape_button.pack(padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)



class Get_Price_FrameManager():

    def pack_forget(self):
        if(self.curr_frame is not None):
            self.curr_frame.pack_forget()

    def pack(self, side):
        if(self.curr_frame is not None):
            self.curr_frame.pack(side=side)
            self.last_pack_side = side
        
    class State(Enum):
        INITIAL = 0
        NEIGHBOURS = 1
        NEURALNETWORK = 2
        NEIGHBOURS_FINISH = 3
        NEURALNETWORK_FINISH = 4

    # Initial Frame where you choose source file and
    # method for price prediction
    class _Initial_Frame(tk.Frame): #TODO enable next button when both file and method has been chosen
        def __init__(self, master, state_change_callback) -> None:
            super().__init__(master)
            self.POSSIBLE_METHOD_NAMES = ["Neural Network", "k-nearest neighbours"]
            self.filename = None
            self.chosen_method = None

            self.choose_file_label = tk.Label(self, text="Select data file:")
            self.choose_file_label.grid(column=0, row=0)

            self.choose_file_button = tk.Button(self, text="Press to select file", command=self._choose_file_pressed)
            self.choose_file_button.grid(column=0, row=1)

            self.chosen_file_label = tk.Label(self, text="No file chosen", fg="red")
            self.chosen_file_label.grid(column=0, row=2)

            self.method_label = tk.Label(self, text="Choose method of choice:")
            self.method_label.grid(column=1, row=0)

            self.method_combobox = ttk.Combobox(self, values=self.POSSIBLE_METHOD_NAMES, state="disabled")
            self.method_combobox.bind("<<ComboboxSelected>>", self._chose_method)
            self.method_combobox.grid(column=1, row=1)

            self.next_button = tk.Button(self, text="Next", command=state_change_callback, state="disabled")
            self.next_button.grid(column=0, row=3, columnspan=2)

        # Should be called only after state_change_callback has been called
        # Otherwise main contain Nones, which are invalid values
        def get_data(self):
            return self.filename, self.chosen_method

        # Saves chosen method from Combobox and allows user to press next button
        def _chose_method(self, event):
            self.chosen_method = event.widget.get()            
            self.next_button.config(state="normal")

        # Prompts user to select .csv data file and saves it
        # Then enables method's Combobox which when selected will at last unlock next button
        def _choose_file_pressed(self):            
            self.filename = fd.askopenfile(
                title='Open data file',
                initialdir= os.getcwd() + '/data/',
                filetypes=(('.csv data files', '*.csv'),)
            )          
            # Display the selected file to the user
            self.chosen_file_label.config(text=f"selected file {self.filename}", fg="green")        

            self.method_combobox.config(state="enabled")

    def _change_state(self):
        if(self.state == self.State.INITIAL):
            #TODO Decide on the selected method to which state go
            #Then show relevant Frame via _set_frame(..., True)
            print("leaving Initial state")
            pass
    
    def _set_frame(self, frame, also_pack=False):
        if(self.curr_frame is not None):
            self.curr_frame.pack_forget()

        self.curr_frame = frame

        if(also_pack):
            self.curr_frame.pack()

    def __init__(self, master) -> None:
        self.state = self.State.INITIAL
        self.curr_frame = None
        self.last_pack_side = None

        # Initialize all possible subframes
        self.initial_frame = self._Initial_Frame(master, self._change_state)

        # Set current frame as intial frame
        self._set_frame(self.initial_frame)