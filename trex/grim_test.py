import subprocess
import shlex



width = 500
height = 300
geometry = f"{10},{10} {width}x{height}"
command = f"grim -g {shlex.quote(geometry)} screen.png"
try:
    subprocess.run(command, shell=True, check=True)
except subprocess.CalledProcessError as e:
    print("Screenshot creating error:", e)

