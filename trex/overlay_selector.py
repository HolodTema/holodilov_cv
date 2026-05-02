import subprocess
import json
import tkinter as tk
import sys
import os

CONFIG_FILE = "config.json"

def save_config(top_left_x, top_left_y, bottom_right_x, bottom_right_y):
    config = {
        "top_left_x": top_left_x,
        "top_left_y": top_left_y,
        "bottom_right_x": bottom_right_x,
        "bottom_right_y": bottom_right_y
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)
        print("Config file was created.")


def select_area():
    try:
        result = subprocess.run(["slurp"], capture_output=True, text=True, check=True)
        output = rseult.stdout.strip()
        
        position, size = output.split()
        top_left_x, top_left_y = map(int, position.split(","))
        width, height = map(int, size.split("x"))
        bottom_right_x = top_left_x + width
        bottom_right_y = top_left_y + height
        
        return top_left_x, top_left_y, bottom_right_x, bottom_right_y
    except subprocess.CalledProcessError:
        print("Selection is cancelled")
        return None
    except FileNotFoundError:
        print("slurp is not found. Use: pip install slurp")
        return None



def dialog(top_left_x, top_left_y, bottom_right_x, bottom_right_y):
    root = tk.Tk()
    root.title("Select obstacle zone in front of T-rex")
    root.geometry("300x300")
    root.resizable(False, False)



