import tkinter as tk
import threading
import time
from queue import Queue


class Overlay:

    def __init__(self):
        self.width = None
        self.height = None
        self.root = None
        self.canvas = None
        self.thread = None
        self.running = False


    def setup_window(self):
        self.root = tk.Tk()
        self.width = self.root.winfo_screenwidth()
        self.height = self.root.winfo_screenheight()

        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', 'black')  
        self.root.geometry(f'{self.width}x{self.height}+0+0')

        self.canvas = tk.Canvas(self.root, highlightthickness=0, bg='black')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.process_commands()


    def process_commands(self):
        try:
            while True:
                cmd, args, kwargs = self.command_queue.get_nowait()
                if cmd == "draw_rect":
                    self.canvas.create_rectangle(*args, **kwargs)
                elif cmd == "clear":
                    self.canvas.delete("all")
                elif cmd == "destroy":
                    self.root.quit()
                    return
        except:
            pass
        if self.running and self.root:
            self.root.after(10, self.process_commands)


    def run_overlay(self):
        self.setup_window()
        self.running = True
        self.root.mainloop()
        self.running = False


    def start(self):
        if self.thread is not None:
            return
        self.thread = threading.Thread(target=self.run_overlay, daemon=True)
        self.thread.start()
        while self.root is None:
            time.sleep(0.01)


    def stop(self):
        if self.root and self.running:
            self.command_queue.put(('destroy', (), {}))
            self.thread = None


    def draw_rect(self, top_left_x, top_left_y, width, height, stroke_width=2, outline='red'):
        bottom_right_x = top_left_x + width
        bottom_right_y = top_left_y + height
        self.canvas.create_rectangle(top_left_x, top_left_y, bottom_right_x, bottom_right_y, outline=outline, width=stroke_width)

    def draw_rect(self, dict_window, stroke_width=2, outline='red'):
        top_left_x = dict_window["left"] - stroke_width
        top_left_y = dict_window["top"] - stroke_width
        bottom_right_x = top_left_x + dict_window["width"] + stroke_width
        bottom_right_y = top_left_y + dict_window["height"] + stroke_width
        self.canvas.create_rectangle(top_left_x, top_left_y, bottom_right_x, bottom_right_y, outline=outline, width=stroke_width)


    def clear(self):
        self.canvas.delete('all')


    def run(self):
        self.root.mainloop()
        
