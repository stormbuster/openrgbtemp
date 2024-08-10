import subprocess
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor

# Function to get CPU temperature using Intel Power Gadget
def get_cpu_temperature():
    result = subprocess.run(
        ["/Applications/Intel Power Gadget/Intel Power Gadget.app/Contents/MacOS/Intel Power Gadget", "-t 1 -a"],
        capture_output=True, text=True
    )
    lines = result.stdout.split("\n")
    for line in lines:
        if "CPU Package Temperature" in line:
            return float(line.split()[-1])
    return None

# Function to interpolate brightness based on temperature
def calculate_brightness(temp):
    if temp <= 45:
        return 0  # 0% brightness at 45°C or lower
    elif temp >= 50:
        return 100  # 100% brightness at 50°C or higher
    else:
        # Linear interpolation between 45°C and 50°C
        return int((temp - 45) * 20)  # 0% to 100% brightness from 45°C to 50°C

# Function to calculate color based on temperature
def calculate_color(temp):
    if temp <= 45:
        return RGBColor(255, 165, 0)  # Orange
    elif temp >= 60:
        return RGBColor(255, 0, 0)  # Red
    else:
        # Interpolate between orange and red
        # (Orange: RGB(255, 165, 0)) to (Red: RGB(255, 0, 0))
        red = 255
        green = int(165 * (60 - temp) / 15)
        blue = 0
        return RGBColor(red, green, blue)

# Connect to the OpenRGB server
client = OpenRGBClient()

# Optional: Load a specific OpenRGB profile if you want
profile_name = 'orange'  # Replace with your actual profile name
client.load_profile(profile_name)

# Get the current CPU temperature
temp = get_cpu_temperature()

# Calculate brightness and color based on temperature
if temp is not None:
    brightness = calculate_brightness(temp)
    color = calculate_color(temp)
else:
    print("Could not retrieve CPU temperature. Setting default color and brightness.")
    brightness = 100  # Default to 100% brightness if temperature retrieval fails
    color = RGBColor(255, 165, 0)  # Default to Orange if temperature retrieval fails

# Apply the calculated color and brightness to all connected devices
for device in client.devices:
    device.set_color(color)
    for led in device.leds:
        led.set_color(color)
        led.set_brightness(brightness)

print(f"CPU Temperature: {temp}°C, Color set to: {color}, Brightness set to: {brightness}%")
