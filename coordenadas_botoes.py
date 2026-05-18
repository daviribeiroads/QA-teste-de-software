import pyautogui
import time

time.sleep(5)  # tempo pra você posicionar o mouse

while True:
    x, y = pyautogui.position()
    print(f"X: {x} Y: {y}", end="\r")
