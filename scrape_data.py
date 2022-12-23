
from ppadb.client import Client
from typing import Tuple, List
import json
import io
import cv2
import numpy as np
import imageio
from scipy.ndimage.filters import maximum_filter
import pytesseract
import time

# user: moonscraper
# pwd: moonscraper 

# constants
CIRCLE_TEMPLATE = imageio.imread("circle.png")
TEMPLATE_H, TEMPLATE_W = CIRCLE_TEMPLATE.shape
FINISH_COLOR = np.array([255, 0, 0, 255])
START_COLOR = np.array([0, 255, 0, 255])
MIDDLE_COLOR = np.array([0, 0, 255, 255])
pytesseract.pytesseract.tesseract_cmd = r"/usr/local/Cellar/tesseract/5.2.0/bin/tesseract"
#Rough bolthole coordinates:
#       A         B          ...   K
# 18   (156, 511) (238, 511)
# 17   (156, 594)  ...
# ...
# 1                                (983, 1919)

def connect_to_device():
    adb = Client(host='127.0.0.1', port=5037)
    devices = adb.devices()
    if len(devices) == 0:
        print("No device attached")
        quit()

    device = devices[0]
    print(f"Connected to device: {device}")
    return device

def mask_color(img: np.array, color: np.array) -> np.array:
    """Return greyscale mask where all occurances
    of `color` in `img` are 1, and everywhere else
    is 0

    Args:
        img (np.array): shape = (N,M,C)
        color (np.array): shape = (C,)
    """

    res = np.zeros(img.shape[:-1], dtype = np.uint8)
    mask = np.all(img == color, axis = -1)
    res[mask] = 255

    return res

def find_circle_pixel_coords(img: np.array, color: np.array) -> Tuple[np.array]:
    """Returns pixel coordinates of center of circles of color
    `color`.

    Args:
        img (np.array): shape = (N,M,C)
        color (np.array): shape = (C,)
    Returns:
        numpy array of shape (num_circles, 2), storing the circle center
        coords in the order (x, y)
    """
    mask = mask_color(img, color)
    res = cv2.matchTemplate(mask, CIRCLE_TEMPLATE, cv2.TM_CCOEFF_NORMED)

    # NMS to remove overlapping detections
    ths = 0.8
    mx = maximum_filter(res, size = (3, 3))
    hp = (res == mx) & (res > ths)
    loc = np.nonzero(hp)
    pts = np.stack(loc[::-1], axis = -1)
    pts[..., 0] += TEMPLATE_H//2 
    pts[..., 1] += TEMPLATE_W//2 
    return pts

def convert_coord_to_code(coord: np.array) -> Tuple[str, int]:
    """Takes in pixel coordinate and returns 
    <letter>-<number> code representing location on moonboard

    Args:
        coord (np.array): Order is (x,y). shape = (2,)
    """
    #print(coord)
    xshift = int(round((coord[0] - 156) / 82.0))
    yshift = int(round((coord[1] - 511)/ 83.0))

    letter = chr(xshift + 65)
    number = 18-yshift

    return letter, number

def get_codes_for_color(img: np.array, color: np.array) -> List[Tuple[str, int]]:
    pts = find_circle_pixel_coords(img, color)
    pts_list = []
    pts_set = set()
    for pt in pts:
        code = convert_coord_to_code(pt)
        if code not in pts_set: # remove any remaining duplicates
            pts_list.append(code)
        pts_set.add(code)
    return sorted(pts_list, key = lambda x: (x[1], x[0]))

def get_basic_climb_info(img: np.array) -> Tuple[str, str, str]:
    """Given a climb screenshot, extract
    climb name, grade, and setter

    Args:
        img (np.array): Climb screenshot
    Returns:
        name, grade, setter
    """
    info = pytesseract.image_to_string(img[129:365, 106:980])
    lines = info.split("\n")
    name, grade = lines[0].split(",")
    grade = grade.strip()
    setter = lines[1].split(":")[1].strip()
    return name, grade, setter

def code_to_string(code: Tuple[str, int]) -> str:
    return code[0] + str(code[1])

def print_hold_list(hold_list: List):
    for i in range(len(hold_list)):
        print(code_to_string(hold_list[i]), end = "")
        if i < len(hold_list) - 1:
            print(", ", end = "")
        else:
            print()

if __name__ == "__main__":
    # Instructions:
    # 1. Open emulator, download moonboard app, and log in. (Pixel 4 API 30)
    # 2. Select desired moonboard layout, then sort all problems from oldest to newest.
    # 3. Change num_problems below to be the number of problems you want to scrape
    # 4. Select the oldest problem and run this script


    # TODO: make this a script with args
    num_problems = 57624
    out_data_path = "2016_data.json"
    save_iter = 100

    device = connect_to_device()
    data = []
    #times = []

    for i in range(num_problems):
        #s = time.time()
        print(20 * "-" + f" Processing climb: {i + 1}/{num_problems} " + 20*"-")
        img = imageio.v2.imread(io.BytesIO(device.screencap())) # shape = (2280, 1080, 4)

        # get hold locations
        start_holds = get_codes_for_color(img, START_COLOR)
        middle_holds = get_codes_for_color(img, MIDDLE_COLOR)
        finish_holds = get_codes_for_color(img, FINISH_COLOR)

        # get climb basic info
        name, grade, setter = get_basic_climb_info(img)
        print(f"Name: {name}\nGrade: {grade}\nSetter: {setter}")
        print(f"Start holds: ", end = "")
        print_hold_list(start_holds)
        print(f"Middle holds: ", end = "")
        print_hold_list(middle_holds)
        print(f"Finish holds: ", end = "")
        print_hold_list(finish_holds)



        # save data
        data.append(
            {
                "setter": setter,
                "grade": grade,
                "name": name,
                "start_holds": start_holds,
                "middle_holds": middle_holds,
                "finish_holds": finish_holds,
            }
        )

        if i % save_iter == 0:
            with open(out_data_path, "w") as f:
                json.dump(data, f, indent=4)

        device.shell("input touchscreen swipe 700 1140 400 1140") # swipe to next 

        # running average for time estimate
        #f = time.time()
        #dt = f - s
        #times.append(dt)
        #est = (sum(times)/len(times)) * (num_problems - (i+1))
        #print(f"Estimated remaining time: {est/3600} hours")

    with open(out_data_path, "w") as f:
        json.dump(data, f, indent=4)