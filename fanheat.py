import subprocess
import time
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor

# Function to get CPU temperature using smc
def get_cpu_temperature():
    try:
        result = subprocess.run(
            ["smc", "list", "-t"],
            capture_output=True, text=True
        )
        
        # Print raw output for debugging
        print("Raw Output from smc:")
        print(result.stdout)
        
        # Parse temperature from the output
        lines = result.stdout.split("\n")
        for line in lines:
            if "TC0P" in line:  # Replace "TC0P" with the appropriate sensor code for CPU temp
                try:
                    parts = line.split()
                    temp_str = parts[-1]
                    temp = float(temp_str.strip('C'))
                    print(f"Parsed Temperature: {temp}°C")
                    return temp
                except ValueError:
                    print("Error parsing temperature value.")
                    return None
        print("Temperature data not found in the output.")
        return None
    except subprocess.CalledProcessError as e:
        print(f"Error executing smc command: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return None

# Function to calculate color based on temperature and brightness
def calculate_color_and_brightness(temp):
    if temp is None:
        print("No temperature data available. Defaulting to Orange with 100% brightness.")
        return RGBColor(255, 165, 0), 100  # Default to Orange at 100% brightness
    
    # Color and brightness thresholds
    min_temp = 45
    max_temp = 60
    min_brightness = 0
    max_brightness = 100
    
    # Color change from orange to red
    if temp < min_temp:
        color = RGBColor(0, 0, 255)  # Blue for temperatures below 45°C
        brightness = 0
    elif temp <= min_temp + 5:
        # Gradient from orange to red
        t = (temp - min_temp) / 5  # Normalize to range [0, 1]
        r = int(255)
        g = int(165 - 165 * t)
        b = int(0)
        color = RGBColor(r, g, b)
        brightness = min_brightness + (temp - min_temp) / (max_temp - min_temp) * (max_brightness - min_brightness)
    elif temp <= max_temp:
        # Gradient from red to a more intense red
        t = (temp - (min_temp + 5)) / (max_temp - (min_temp + 5))  # Normalize to range [0, 1]
        color = RGBColor(255, 0, 0)
        brightness = min_brightness + (temp - min_temp) / (max_temp - min_temp) * (max_brightness - min_brightness)
    else:
        color = RGBColor(128, 0, 128)  # Purple for temperatures above 60°C
        brightness = max_brightness
    
    print(f"Calculated Color: {color} with Brightness: {brightness}%")
    return color, brightness

# Connect to the OpenRGB server
print("Attempting to connect to OpenRGB server...")
client = OpenRGBClient()
print("Connected to OpenRGB server.")

# Continuously monitor temperature and update LED color
try:
    while True:
        # Get the current CPU temperature
        temp = get_cpu_temperature()

        # Calculate the desired color and brightness based on temperature
        color, brightness = calculate_color_and_brightness(temp)

        # Apply the calculated color and brightness to the first connected device
        try:
            device = client.devices[0]  # Assuming it's the first device
            print(f"Applying color and brightness to device {device.name}...")

            # Set the color for all LEDs in the device
            # Note: Adjusting brightness might require different handling depending on your device
            device.set_color(color)
            device.set_brightness(brightness / 100)  # Assuming brightness needs to be a fraction

            print(f"Color {color} with brightness {brightness}% applied to device {device.name}.")
        except Exception as e:
            print(f"Failed to apply settings: {e}")

        # Wait for 10 seconds before the next update
        time.sleep(10)

except KeyboardInterrupt:
    print("Script interrupted by user.")
