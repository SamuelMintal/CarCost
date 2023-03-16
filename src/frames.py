# 3rd party imports
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import ttk
import os
from enum import Enum
import pandas as pd


# Custom files import
from scraper import *
from predicors import *

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

        about_text = \
        "1. Scrape the data on frame accessed by clicking on \"Choose Car\" button.\n\
You can always watch the scraping process on the Chrome tab the program opens with.\n\
2.) Then press \"Get Price\" button and choose from which file ~ car model you want\n\
to predict price. Then choose desired prediction method and continue filling the fields \n\
3.) until you get window with the predicted price of the car you entered.\n\
4.) As you are now done you can exit the program by pressing \"Exit\" button"
        
        self.about_label = tk.Label(self, text=about_text)
        self.about_label.pack(padx=10, pady=10)
    


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

    # start scrapeing and save it into data/brand_model.csv
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

        # scraper button
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
        CAR_PARAMS = 1
        NEIGHBOURS = 2
        NEURALNETWORK = 3
        NEIGHBOURS_FINISH = 4
        NEURALNETWORK_FINISH = 5

    # Initial Frame where you choose source file and
    # method for price prediction
    class _Initial_Frame(tk.Frame): # Enable next button when both file and method has been chosen
        def __init__(self, master, forward_state_change_callback) -> None:
            super().__init__(master)
            self.POSSIBLE_METHOD_NAMES = ["Neural Network", "k-nearest neighbours"]
            self.file_path = None
            self.chosen_method = None

            WIDGETS_PADDING_X = 5
            WIDGETS_PADDING_Y = 5 

            self.choose_file_label = tk.Label(self, text="Select data file:")
            self.choose_file_label.grid(column=0, row=0, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            self.choose_file_button = tk.Button(self, text="Press to select file", command=self._choose_file_pressed)
            self.choose_file_button.grid(column=0, row=1, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            self.chosen_file_label = tk.Label(self, text="No file chosen", fg="red")
            self.chosen_file_label.grid(column=0, row=2, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            self.method_label = tk.Label(self, text="Choose method of choice:")
            self.method_label.grid(column=1, row=0, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            self.method_combobox = ttk.Combobox(self, values=self.POSSIBLE_METHOD_NAMES, state="disabled")
            self.method_combobox.bind("<<ComboboxSelected>>", self._chose_method)
            self.method_combobox.grid(column=1, row=1, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            self.next_button = tk.Button(self, text="Next", command=forward_state_change_callback, state="disabled")
            self.next_button.grid(column=0, row=3, columnspan=2, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

        # Should be called only after state_change_callback has been called
        # Otherwise main contain Nones, which are invalid values
        def get_data(self):
            return self.file_path, self.chosen_method

        # Saves chosen method from Combobox and allows user to press next button
        def _chose_method(self, event):
            self.chosen_method = event.widget.get()            
            self.next_button.config(state="normal")

        # Prompts user to select .csv data file and saves it
        # Then enables method's Combobox which when selected will at last unlock next button
        def _choose_file_pressed(self):            
            self.file_path = fd.askopenfile(
                title='Open data file',
                initialdir= os.getcwd() + '/data/',
                filetypes=(('.csv data files', '*.csv'),)
            ).name         
            # Display the selected file to the user
            self.chosen_file_label.config(text=f"selected file {self.file_path.split('/')[-1]}", fg="green")        

            self.method_combobox.config(state="readonly")

    # Frame for entering parameters of car which price we want to predict
    # Gets possible values of transmission and fuel from previously selected .csv file
    class _Car_Params_Frame(tk.Frame):

        def __init__(self, master, forward_state_change_callback, backward_state_change_callback, source_csv_file=None) -> None:
            super().__init__(master)
            WIDGETS_PADDING_X = 5
            WIDGETS_PADDING_Y = 5 

            #save callback for usage in self._next_pressed
            self.forward_state_change_callback=forward_state_change_callback
                
            # Construct all the widgets
            # And set them empty

            # Instruction's widgets
            self.instruction_label = tk.Label(self, text="Now enter the parameters of car which price you want to estimate")
            self.instruction_label.grid(column=0, row=0, columnspan=2, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            # Manufacture year widgets
            self.manufacture_year_label = tk.Label(self, text="Enter the year of manufacture:")
            self.manufacture_year_label.grid(column=0, row=1, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)
            self.manufacture_year_entry = tk.Entry(self)
            self.manufacture_year_entry.grid(column=1, row=1, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            # Transmission type widgets
            self.trans_type_label = tk.Label(self, text="Enter transmission type:")
            self.trans_type_label.grid(column=0, row=2, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)
            self.trans_type_combobox = ttk.Combobox(self, values=[])
            self.trans_type_combobox.grid(column=1, row=2, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            # Fuel type widgets
            self.fuel_type_label = tk.Label(self, text="Enter fuel type:")
            self.fuel_type_label.grid(column=0, row=3, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)
            self.fuel_type_combobox = ttk.Combobox(self, values=[])
            self.fuel_type_combobox.grid(column=1, row=3, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            # Mileage widgets
            self.mileage_label = tk.Label(self, text="Enter the mileage:")
            self.mileage_label.grid(column=0, row=4, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)
            self.mileage_entry = tk.Entry(self)
            self.mileage_entry.grid(column=1, row=4, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            # Power (kw) widgets
            self.power_label = tk.Label(self, text="Enter power (kw):")
            self.power_label.grid(column=0, row=5, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)
            self.power_entry = tk.Entry(self)
            self.power_entry.grid(column=1, row=5, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            # Back and Next Buttons
            self.back_button = tk.Button(self, text="Back", command=backward_state_change_callback)
            self.back_button.grid(column=0, row=6, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)
            self.next_button = tk.Button(self, text="Next", command=self._next_pressed)
            self.next_button.grid(column=1, row=6, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            # Now set possible values for Comboboc widgets
            # And clear Entry widgets
            self.set_possible_vals(source_csv_file)

        # Resets chosen parameters and sets possible values of Comboboxes so they
        # correspond to the specified csv file (only for transmission and fuel)
        def set_possible_vals(self, source_csv_file):
            # Clear Entry widgets
            self.manufacture_year_entry.delete(0, 'end')
            self.mileage_entry.delete(0, 'end')
            self.power_entry.delete(0, 'end')
            
            # Set the combobox widget possible values
            if(source_csv_file is None):
                return
            data = pd.read_csv(source_csv_file)
            self.trans_type_combobox.config(values=list(data["trans"].unique()))
            self.fuel_type_combobox.config(values=list(data["fuel"].unique()))
            
        # Returns dictionary describing the entered car
        def get_data(self):
            return {
                "price": None,
                "year":  self.manufacture_year_entry.get(), 
                "trans": self.trans_type_combobox.get(),
                "fuel":  self.fuel_type_combobox.get(),
                "km":    self.mileage_entry.get(),
                "kw":   self.power_entry.get(),
            }
            
        def _next_pressed(self):
            # Check if inputted data are valid
            entered_man_year = self.manufacture_year_entry.get()
            entered_mileage = self.mileage_entry.get()
            entered_power = self.power_entry.get()

            if(
                entered_man_year.isnumeric() and int(entered_man_year) >= 0 and
                entered_mileage.isnumeric() and int(entered_mileage) >= 0 and
                entered_power.isnumeric() and int(entered_power) >= 0
                ):
                # Inputted data are valid
                # Therefore call forward_state_change_callback
                self.forward_state_change_callback()
            else:
                # Inputted data are invalid
                # Therefore throw error and do not move forward
                messagebox.showerror("Error", "invalid data entered into entries\nchange them to continue")
                return            


    # Frame for choosing k-nearest neighbours method parameters
    class _Neighbours_Frame(tk.Frame):
        def __init__(self, master, forward_state_change_callback, backward_state_change_callback, car_to_predict=None, file_path=None) -> None:
            super().__init__(master)
            WIDGETS_PADDING_X = 5
            WIDGETS_PADDING_Y = 5 

            self.file_path = file_path
            self.car_to_predict = car_to_predict
            self.forward_state_change_callback = forward_state_change_callback

            self.choose_k_label = tk.Label(self, text="Choose value of k:")
            self.choose_k_label.grid(column=0, row=0, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            self.k_value_entry = tk.Entry(self)
            self.k_value_entry.grid(column=1, row=0, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            # Start button
            self.start_button = tk.Button(self, text="Start", command=self._start_pressed)
            self.start_button.grid(column=1, row=1, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)
            # Back button
            self.back_button = tk.Button(self, text="Back", command=backward_state_change_callback)
            self.back_button.grid(column=0, row=1, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

        def set_params(self, car_to_predict, file_path):
            self.car_to_predict = car_to_predict
            self.file_path = file_path

        def _start_pressed(self):
            # Check if k is valid and self.car_to_predict to be set
            k_val = self.k_value_entry.get()
            if(not(k_val.isnumeric() and int(k_val) > 0)):
                messagebox.showerror("Error", "invalid k value entered \n change it to continue")

            # Run k-nearest neighbours algo and report its result.
            predicted_price = K_nearest_neighbours.predict_price_of(self.car_to_predict, self.file_path, k=int(k_val))
            messagebox.showinfo("Result", f"Predicted price of the entered car is {predicted_price:.2f} Euros.")
            self.forward_state_change_callback()

    # Frame for setting and running neural network predictor
    class _Neural_Network_Frame(tk.Frame):
        def __init__(self, master, forward_state_change_callback, backward_state_change_callback, car_to_predict=None, file_path=None) -> None:
            super().__init__(master)
            WIDGETS_PADDING_X = 5
            WIDGETS_PADDING_Y = 5 

            self.forward_state_change_callback = forward_state_change_callback
            self.car_to_predict = car_to_predict
            self.file_path = file_path

            self.architecture_label = tk.Label(self, text="Enter NN architecture as sequence of space separated positive numbers")
            self.architecture_label.grid(row=0, column=0, columnspan=2, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            self.architecture_entry = tk.Entry(self, text="")
            self.architecture_entry.grid(row=1, column=0, columnspan=2, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            self.epochs_label = tk.Label(self, text="Enter number of epochs for NN to be trained for")
            self.epochs_label.grid(row=2, column=0, columnspan=2, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            self.epochs_entry = tk.Entry(self, text="")
            self.epochs_entry.grid(row=3, column=0, columnspan=2, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

            self.back_button = tk.Button(self, text="Back", command=backward_state_change_callback)
            self.back_button.grid(column=0, row=4, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)
            self.start_button = tk.Button(self, text="Start", command=self._start_pressed)
            self.start_button.grid(column=1, row=4, padx=WIDGETS_PADDING_X, pady=WIDGETS_PADDING_Y)

        def set_params(self, car_to_predict, file_path):
            self.car_to_predict = car_to_predict
            self.file_path = file_path

        def _start_pressed(self):
            entered_arch = self.architecture_entry.get().split()
            if(len(entered_arch) == 0):
                messagebox.showerror("Error", "invalid architecture entered \n it needs to be nonzero length. Change it to continue")
                return
            
            res_arch = []
            for n_neurons in entered_arch:
                if(str.isnumeric(n_neurons) and int(n_neurons) > 0):
                    res_arch.append(int(n_neurons))
                else:
                    messagebox.showerror("Error", "invalid architecture entered \n all values needs to be positive numbers. Change it to continue")
                    return
                
            n_epochs = self.epochs_entry.get()
            if(str.isnumeric(n_epochs) and int(n_epochs) > 0):
                n_epochs = int(n_epochs)
            else:
                messagebox.showerror("Error", "invalid epochs entered \n it needs to be positive number. Change it to continue")
                return
                
            # Now that I have all the values checked I can run the NN predictor
            nn_predictor = Neural_network_predictor(res_arch, n_epochs, self.file_path)
            predicted_price = nn_predictor.predict_price_of(self.car_to_predict)
            messagebox.showinfo("Result", f"Predicted price of the entered car is {predicted_price:.2f} Euros.")

            self.forward_state_change_callback()

    def _change_state_backward(self):
        match self.state:
            case self.State.CAR_PARAMS:
                print("State change: Car Params state -> Initial state")
                self.state = self.State.INITIAL
                self._set_frame(self.initial_frame, also_pack=True)
            
            case self.State.NEIGHBOURS:
                print("State change: Neighbours state -> Car Params state")
                self.state = self.State.CAR_PARAMS
                self._set_frame(self.car_params_frame, also_pack=True)

            case self.State.NEURALNETWORK:
                print("State change: Neural Network state -> Car Params state")
                self.state = self.State.CAR_PARAMS
                self._set_frame(self.car_params_frame, also_pack=True)

    def _change_state_forward(self):
        # Decide to which state go
        # Then show relevant Frame via _set_frame(..., True)

        match self.state:
            case self.State.INITIAL:
                print("State change: Initial state -> Car Params state")
                # Get data from initial frame
                self.file_path, self.chosen_method = self.curr_frame.get_data()
                # Change self.state and set values for new frame  
                self.state = self.State.CAR_PARAMS
                self._set_frame(self.car_params_frame, also_pack=True)
                #And let it know .csv file in order for it to pull data from it
                self.curr_frame.set_possible_vals(self.file_path)

            case self.State.CAR_PARAMS:
                entered_car = self.curr_frame.get_data()
                if(self.chosen_method == "k-nearest neighbours"):
                    print("State change: Car Params state -> Neighbours state")
                    self.state = self.State.NEIGHBOURS
                    self._set_frame(self.neighbours_frame, also_pack=True)
                    self.neighbours_frame.set_params(entered_car, self.file_path)
                elif(self.chosen_method == "Neural Network"):
                    print("State change: Car Param state -> Neural Network state")
                    self.state = self.State.NEURALNETWORK
                    self._set_frame(self.nn_frame, also_pack=True)
                    self.nn_frame.set_params(entered_car, self.file_path)
                    
    
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
        self.chosen_method = None
        self.file_path = None

        # Initialize all possible subframes
        self.initial_frame = self._Initial_Frame(master, self._change_state_forward)
        self.car_params_frame = self._Car_Params_Frame(master, self._change_state_forward, self._change_state_backward)
        self.neighbours_frame = self._Neighbours_Frame(master, self._change_state_forward, self._change_state_backward)
        self.nn_frame = self._Neural_Network_Frame(master, self._change_state_forward, self._change_state_backward)
        # Set current frame as intial frame
        self._set_frame(self.initial_frame)