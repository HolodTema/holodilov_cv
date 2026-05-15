import tkinter as tk
import threading
import queue
import time


class Overlay:
    def __init__(self):
        self.width = None
        self.height = None
        self.root = None
        self.canvas = None
        self.thread = None
        self.running = False
        self.cmd_queue = queue.Queue()

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
                cmd, args, kwargs, result_q = self.cmd_queue.get_nowait()
                if cmd == "draw_rect":
                    coords, style = args
                    canvas_id = self.canvas.create_rectangle(*coords, **style)
                    if result_q:
                        result_q.put(canvas_id)
                elif cmd == "delete_item":
                    canvas_id = args[0]
                    self.canvas.delete(canvas_id)
                elif cmd == "clear_all":
                    self.canvas.delete("all")
                elif cmd == "destroy":
                    self.root.quit()
                    return
        except queue.Empty:
            pass
        if self.running and self.root:
            self.root.after(10, self.process_commands)

    def run_overlay(self):
        self.running = True
        self.setup_window()
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
            self.cmd_queue.put(('destroy', (), {}, None))
            self.thread = None

    def _send_sync_command(self, cmd, args=()):
        result_q = queue.Queue()
        self.cmd_queue.put((cmd, args, {}, result_q))
        return result_q.get(timeout=1.0)

    def draw_rect(self, top_left_x, top_left_y, width, height,
                  stroke_width=2, outline='red'):
        coords = (top_left_x, top_left_y, top_left_x + width, top_left_y + height)
        style = {'outline': outline, 'width': stroke_width}
        return self._send_sync_command('draw_rect', (coords, style))

    def draw_rect_from_dict(self, dict_window, stroke_width=2, outline='red'):
        left = dict_window["left"] - stroke_width
        top = dict_window["top"] - stroke_width
        right = left + dict_window["width"] + stroke_width
        bottom = top + dict_window["height"] + stroke_width
        coords = (left, top, right, bottom)
        style = {'outline': outline, 'width': stroke_width}
        return self._send_sync_command('draw_rect', (coords, style))

    def clear_by_canvas_id(self, canvas_id):
        self.cmd_queue.put(('delete_item', (canvas_id,), {}, None))

    def clear_all(self):
        self.cmd_queue.put(('clear_all', (), {}, None))

