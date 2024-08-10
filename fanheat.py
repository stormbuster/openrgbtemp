import subprocess
import sys
import os
import logging

# Import the necessary modules after activation
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor
import time
import subprocess
from openrgb import OpenRGBClient
from openrgb.utils import RGBColor

# Function to get CPU temperature using smc
def get_cpu_temperature():
    try:
        result = subprocess.run(["/Applications/Stats.app/Contents/Resources/smc", "list", "-t"], capture_output=True, text=True)
      
        # Print raw output for debugging
        # print("Raw Output from smc:")
        # print(result.stdout)
        
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

# Function to calculate color based on temperature
def calculate_color(temp):
    if temp is None:
        print("No temperature data available. Defaulting to Black.")
        return RGBColor(0, 0, 0)  # Default to Black
    
    # Define temperature ranges
    orange_start_temp = 50
    orange_end_temp = 55
    red_start_temp = 55
    red_end_temp = 70

    # Determine color
    if temp <= orange_start_temp:
        color = RGBColor(0, 0, 0)  # Black
    elif temp <= orange_end_temp:
        # Transition from black to full orange
        t = (temp - orange_start_temp) / (orange_end_temp - orange_start_temp)  # Normalize to range [0, 1]
        t = max(0, min(t, 1))  # Clamp t to [0, 1]
        r = 255
        g = int(165 * t)  # Transition from 0 to 165 (Orange component)
        b = 0
        color = RGBColor(r, g, b)
    elif temp <= red_end_temp:
        # Transition from orange to red
        t = (temp - red_start_temp) / (red_end_temp - red_start_temp)  # Normalize to range [0, 1]
        t = max(0, min(t, 1))  # Clamp t to [0, 1]
        r = 255
        g = int(165 * (1 - t))  # Transition from 165 (Orange component) to 0
        b = 0
        color = RGBColor(r, g, b)
    else:
        color = RGBColor(255, 0, 0)  # Full red

    print(f"Calculated Color: {color}")
    return color

# Connect to the OpenRGB server
print("Attempting to connect to OpenRGB server...")
client = OpenRGBClient()
print("Connected to OpenRGB server.")

# Continuously monitor temperature and update LED color
try:
    while True:
        # Get the current CPU temperature
        temp = get_cpu_temperature()

        # Calculate the desired color based on temperature
        color = calculate_color(temp)

        # Apply the calculated color to the first connected device
        try:
            device = client.devices[0]  # Assuming it's the first device
            # print(f"Applying color to device {device.name}...")

            # Apply the color
            device.set_color(color)
            print(f"Color {color} applied to device {device.name} for temp {temp}")
                
        except Exception as e:
            # print(f"Failed to apply settings: {e}")

        # Wait for 10 seconds before the next update
        time.sleep(1)

except KeyboardInterrupt:
    print("Script interrupted by user.")
