import subprocess
import json
import os
from pathlib import Path



def save_config_file(area):
    path = Path(__file__).parent / "config.json"
    with path.open("w") as f:
        json.dump(area, f)



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



def main():
    print("Select game window:")
    area = select_area_with_slurp()
    save_config_file(area)
    print("Success! Created file config.json")



if __name__ == "__main__":
    main()




