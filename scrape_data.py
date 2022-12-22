
from ppadb.client import Client


def connect_to_device():
    adb = Client(host='127.0.0.1', port=5037)
    devices = adb.devices()
    if len(devices) == 0:
        print("No device attached")
        quit()

    device = devices[0]
    print(f"Connected to device: {device}")
    return device

if __name__ == "__main__":
    # Instructions:
    # 1. Open emulator, download moonboard app, and log in. 
    # 2. Select desired moonboard layout, then sort all problems from oldest to newest.
    # 3. Change num_problems below to be the number of problems you want to scrape
    # 4. Select the oldest problem and run this script

    num_problems = 57619
    device = connect_to_device()

    for i in range(num_problems):
        image = device.screencap() # take screencap and save 

        #with open(f"2016_screenshots/problem_{i:05d}.png", 'wb') as f:
            #f.write(image)
        device.shell("input touchscreen swipe 700 1140 400 1140") # swipe to next 