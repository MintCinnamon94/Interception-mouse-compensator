import os
import interception
import win32api
import win32con
import pydirectinput
import mouse
import keyboard
import pynput
import random
import pyautogui
import tkinter as tk
import threading
import time
from tkinter import Tk
from time import sleep
from threading import Thread

#     ----- Global variables -----
MFont = ("Arial", 10)
weapon_A_compensation = False

#     ----- Weapon patterns -----
weapon_A_pattern = [(0,48),(0,46),(0,44),(0,42),(-2,35),
                    (-3,32),(-2,30),(-1,28),(0,25),(1,24),
                    (2,22),(0,20),(0,18),(0,15),(0,12),(0,10)]# 16 shots from weapon_A

weapon_B_pattern = [(0, 35), (0, 32), (-2, 30), (-3, 28), (-4, 25),
                    (-3, 22), (-1, 20), (2, 18), (4, 16), (5, 15),
                    (4, 14), (2, 13), (0, 12), (-2, 11), (-4, 10),
                    (-3, 9), (-1, 8), (1, 8), (2, 7), (3, 7)]

class GuiWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ---- How to add an image to the background ----
        self.bg_image = tk.PhotoImage(file="images/Logo.png")
        self.bglogo = tk.Label(self, image=self.bg_image)
        self.bglogo.place(x=0, y=0, relwidth=1, relheight=1)
        # ---- Gui Size and title ----
        self.title("Input Compensation")
        self.geometry("200x600")
        self.resizable(False,False)
        # ---- How to make the -Container inside the application Window- ----
        self.MyGui = tk.Frame(self)
        self.MyGui.grid(row=0, column=0)
        # ---- How to add a title INSIDE the Gui ----
        self.label = tk.Label(self.MyGui, text="toggles", font=MFont)
        self.label.pack(padx=0)

        # ---- Weapon variables ----
        self.weapon_A_compensation = tk.BooleanVar(value=False) # Hold memory allowing .get in "weapon_A_function"
        self.weapon_A_chkbox = tk.Checkbutton(
            self.MyGui,
            text="Weapon A Compensation",
            variable=self.weapon_A_compensation,
            command=lambda: self.weapon_A_function(),
            font=MFont)
        self.weapon_A_chkbox.pack(pady=5)

        self.weapon_B_compensation = tk.BooleanVar(value=False) # Hold memory allowing .get in "weapon_B_function"
        self.weapon_B_chkbox = tk.Checkbutton(
            self.MyGui,
            text="Weapon B Compensation",
            variable=self.weapon_B_compensation,
            command=lambda: self.weapon_B_function(),
            font=MFont)
        self.weapon_B_chkbox.pack(pady=5)

        # ---- Functions for checking 1 checkbox at a time ----
    def weapon_A_function(self):
        if self.weapon_A_compensation.get() == 1:
            self.weapon_B_compensation.set(0)

        print(f'Weapon A: {self.weapon_A_compensation.get()} | Weapon B: {self.weapon_B_compensation.get()}')

        # ---- Function for checkbox 2 "weapon_B" ----
    def weapon_B_function(self):
        if self.weapon_B_compensation.get() == 1:
            self.weapon_A_compensation.set(0)

        print(f'Weapon A: {self.weapon_A_compensation.get()} | Weapon B: {self.weapon_B_compensation.get()}')

        # ---- Compensation loop for Weapon A ----
def weapon_compensation_loop(app):
    time.sleep(1)
    try:
        interception.auto_capture_devices(mice=True)
    except Exception as e:
        print(f"driver error {e}")
    shot_count = 0
    last_shot = 0

    while True:
        # ---- How to set a keybind toggle ----
        if keyboard.is_pressed('8'):
            current = app.weapon_A_compensation.get()
            app.weapon_A_compensation.set(not current)
            app.weapon_A_function()
            while keyboard.is_pressed('8'):time.sleep(0.01)
          
        if keyboard.is_pressed('9'):
            current = app.weapon_B_compensation.get()
            app.weapon_B_compensation.set(not current)
            app.weapon_B_function()
            while keyboard.is_pressed("9"):time.sleep(0.01)

        is_firing = win32api.GetAsyncKeyState(0x01) != 0
        is_aiming = win32api.GetAsyncKeyState(0x02) != 0

        if app.weapon_A_compensation.get():
            # ---- How to set script to only fire while aiming ----
            if is_aiming != 0 and is_firing != 0:

                if shot_count < len(weapon_A_pattern): # ---- Measures the length of the pattern (how many shots total) ----
                    move_x, move_y = weapon_A_pattern[shot_count] # ---- Making move_x, move_y variables for pattern ----
                    interception.move_relative(move_x, move_y + random.randint(-1,1))
                    shot_count += 1 # ---- Shot counter for magazine size ----
                    last_shot = time.time() # ---- Adding a time tracker for later in the code ----
                    print(f'{shot_count}') # ---- Shows shot counter in IDE for verification of place in magazine ----
                    time.sleep(0.01)
                    while win32api.GetAsyncKeyState(0x01) != 0: # ---- This while statement allows click firing vs holding LMB (semi auto vs auto) ----
                        time.sleep(0.01)
        if is_aiming != 0 and is_firing == 0:
            if time.time() - last_shot > 0.20: # ---- Timer for when the last shot was fired so it can reset to 0 ----
                shot_count = 0 # ---- Resets shot count (place in magazine) to 0 if time parameters are met ----
        if  is_aiming == 0: # ---- If you stop aiming shot count is reset back to 0 ----
            shot_count = 0

        # ---- Compensation logic for weapon_B ----
        elif app.weapon_B_compensation.get() == 1:
            # ---- Only works if you're aiming and firing ----
            if is_firing != 0 and is_aiming != 0:
                # ---- mouse movement using global variable weapon_B_pattern stated above ----
                if shot_count < len(weapon_B_pattern):
                    move_x, move_y = weapon_B_pattern[shot_count] # ---- move_x, move_y = weapon_B_pattern variable for spray pattern
                    interception.move_relative(move_x, int(move_y + random.uniform(-0.5,0.5))) # ---- Interceptions acts as a physical usb device ----
                    shot_count = (shot_count + 1) % len(weapon_B_pattern) # ---- Infinite loop using "Modolu "%"" resetting shot pattern to 0 if held passed full magazine size ----
                    print(f'{shot_count + 1}') # ---- Prints location in magazine in IDE for testing purposes ----
                    last_shot = time.time() # ---- last_shot variable as a time stamp for if function below allowing shot counter to reset if "X seconds" is reached (recoil reset) ----
                    time.sleep(0.06)
                    # ---- If you're firing and aiming but not shooting for 0.80s shot counter resets to 0 ----
            if is_aiming and is_firing == 0:
                if time.time() - last_shot > 0.80:
                    shot_count = 0
                    # ---- Resets shot count when not aiming ----
            if is_aiming == 0:
                shot_count = 0
                time.sleep(0.01)
        #elif # ---- continue to next weapon ----
if __name__=='__main__':
    app = GuiWindow()
    threading.Thread(target=weapon_compensation_loop, args=(app,), daemon=True).start()
    app.mainloop()
