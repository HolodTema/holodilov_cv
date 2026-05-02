import subprocess
import json
import tkinter as tk
import sys
import os
from pathlib import Path



def save_config_file(x_top_left, y_top_left, x_bottom_right, y_bottom_right):
    path = Path(__file__).parent / "config.json"
    config = {
        "x_top_left": x_top_left,
        "y_top_left": y_top_left,
        "x_bottom_right": x_bottom_right,
        "y_bottom_right": y_bottom_right,
    }
    with path.open("w") as f:
        json.dump(config, f)



def select_area_with_slurp():
    try:
        result = subprocess.run(["slurp"], capture_output=True, text=True, check=True)
        output = result.stdout.strip()

        position, size = output.split(" ")
        x, y = map(int, position.split(","))
        width, height = map(int, size.split("x"))
        x_bottom_right = x + width
        y_bottom_right = y + height
        return {
            "x_top_left": x,
            "y_top_left": y,
            "x_bottom_right": x_bottom_right,
            "y_bottom_right": y_bottom_right
        }
    except subprocess.CalledProcessError:
        print("Selection overlay to select game window is cancelled")
        return None
    except FileNotFoundError:
        print("No slurp program found")
        return None



def confirmation_dialog(area):
    root = tk.Tk()
    root.title("Confirm size of game window")
    root.geometry("300x300")
    root.resizable(False, False)

    tk.Label(root, text="Выделена область игры.").pack(pady=5)
    tk.Label(root, text="Теперь укажите зону, где появляются\nпрепятствия (перед динозавром).").pack(pady=5)

    tk.Label(root, text="Левый X (check_x1):").pack(pady=(10,0))
    entry_x1 = tk.Entry(root)
    entry_x1.insert(0, str(area["x_top_left"]))
    entry_x1.pack()

    tk.Label(root, text="Правый X (check_x2):").pack(pady=(5,0))
    entry_x2 = tk.Entry(root)
    entry_x2.insert(0, str(area["x_bottom_right"]))
    entry_x2.pack()

    tk.Label(root, text="Y уровня земли (check_y):").pack(pady=(5,0))
    entry_y = tk.Entry(root)
    entry_y.insert(0, str(area["y_top_left"]))
    entry_y.pack()

    def on_ok():
        try:
            x1 = int(entry_x1.get())
            x2 = int(entry_x2.get())
            y = int(entry_y.get())
            if x1 >= x2:
                messagebox.showerror("Ошибка", "check_x1 должно быть меньше check_x2")
                return
            save_config_file(x1, y, x2, y + 30)
            root.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите целые числа")

    tk.Button(root, text="✅ Сохранить", command=on_ok).pack(pady=15)
    root.mainloop()



def main():
    print("Select game window:")
    area = select_area_with_slurp()
    if area:
        confirmation_dialog(area)
    else:
        print("Unable to select game window")
        sys.exit(1)




if __name__ == "__main__":
    main()




