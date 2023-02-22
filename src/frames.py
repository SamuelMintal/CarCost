# 3rd party imports
import tkinter as tk
from tkinter import ttk
import os

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



class Get_Price_Frame(tk.Frame):

    # Initial Frame where you choose source file and
    # method for price prediction
    class _Initial_Frame(tk.Frame):
        def __init__(self, master) -> None:
            super().__init__(master)

        # depack all widgets
        def depack(self):
            pass

    def __init__(self, master) -> None:
        super().__init__(master)