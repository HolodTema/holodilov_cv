from snippingtool import SnippingTool
import ctypes
import json
from pathlib import Path



def save_config_file(area):
    path = Path(__file__).parent / "config.json"
    with path.open("w") as f:
        json.dump(area, f)


def select_area():
    # to work in physics pixels, not in virtual (dp) pixels
    ctypes.windll.user32.SetProcessDPIAware()
    
    snipping = SnippingTool()
    _, bbox = snipping.capture()
    area = {
        "left": bbox[0],
        "top": bbox[1],
        "width": bbox[2],
        "height": bbox[3]
    }
    return area


def main():
    area = select_area()
    save_config_file(area)


if __name__ == "__main__":
    main()
    

