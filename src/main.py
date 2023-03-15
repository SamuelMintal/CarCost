# 3rd party imports
import tkinter as tk
import numpy as np
import tensorflow as tf
# Custom files imports
from frames import *


class Car_Cost(tk.Tk):

    def _change_main_frame_to(self, frame):
        if(self.main_frame != frame):
            self.main_frame.pack_forget()
            self.main_frame = frame
            self.main_frame.pack(side = tk.LEFT)

    def _about_pressed(self):
        self._change_main_frame_to(self.about_frame)

    def _choose_car_pressed(self):
        self._change_main_frame_to(self.car_choose_frame)
        #self.main_frame.refresh_offerings_data()

    def _get_price_pressed(self):
        self._change_main_frame_to(self.get_price_frame)

    def __init__(self, screenName: str = "Car Cost", baseName: str | None = None, className: str = " Car Cost", useTk: bool = True, sync: bool = False, use: str | None = None) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)
        FRAMES_PADDING_X = 10
        FRAMES_PADDING_Y = 10

        self.car_choose_frame = Car_Choose_Frame(self)
        self.about_frame = About_Frame(self)
        self.get_price_frame = Get_Price_FrameManager(self)

        #Set up Buttons_Frame
        button_names = [ "About", "Choose car", "Get price", "Exit"]
        button_actions = [self._about_pressed, self._choose_car_pressed, self._get_price_pressed, self.destroy]
        self.buttons_frame = Buttons_Frame(self, button_names, button_actions)

        #Display buttons frame
        self.buttons_frame.pack(side=tk.LEFT, padx=FRAMES_PADDING_X, pady=FRAMES_PADDING_Y)
        #Display defualt main frame
        self.main_frame = self.about_frame
        self.main_frame.pack(side=tk.LEFT, padx=FRAMES_PADDING_X, pady=FRAMES_PADDING_Y)



def k_nearest_main():
    car_cost_app = Car_Cost()
    car_cost_app.mainloop()

if __name__ == "__main__":
    k_nearest_main()