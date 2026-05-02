import tkinter as tk

class SnippingTool:
    def __init__(self):
        self.start_x = None
        self.start_y = None
        self.rect_id = None

        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.attributes('-alpha', 0.3)  # Полупрозрачный оверлей
        self.root.configure(cursor='cross')
        self.canvas = tk.Canvas(self.root, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.bind('<ButtonPress-1>', self.on_press)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        self.canvas.bind('<ButtonRelease-1>', self.on_release)

        self.root.mainloop()

    def get_corrected_coords(self, x1, y1, x2, y2):
        if x1 < x2:
            left, right = x1, x2
        else:
            left, right = x2, x1

        if y1 < y2:
            top, bottom = y1, y2
        else:
            top, bottom = y2, y1
        return left, top, right, bottom

    def on_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect_id:
            self.canvas.delete(self.rect_id)

    def on_drag(self, event):
        if self.rect_id:
            self.canvas.delete(self.rect_id)
        # Рисуем прямоугольник между начальной и текущей точками
        self.rect_id = self.canvas.create_rectangle(self.start_x, self.start_y,
                                                    event.x, event.y,
                                                    outline='red', width=2)

    def on_release(self, event):
        x1, y1, x2, y2 = self.start_x, self.start_y, event.x, event.y
        # Корректируем координаты на случай выделения справа-налево или снизу-вверх
        left, top, right, bottom = self.get_corrected_coords(x1, y1, x2, y2)

        # (left, top) — это x, y, (right-left) — это width, а (bottom-top) — height
        print(f'Вы выбрали область: x={left}, y={top}, width={right-left}, height={bottom-top}')
        self.root.quit()

if __name__ == '__main__':
    SnippingTool()
    