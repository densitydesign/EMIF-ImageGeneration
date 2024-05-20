import os
import requests
import base64
from api_parameters_img2img import img2img_data
from PIL import Image
import io
from tqdm import tqdm
import time
import psutil
import csv

# Define the URL of the API endpoint

url_img2img = "http://127.0.0.1:7860/sdapi/v1/img2img"

# Prompt the user to choose their device
device_choice = input("Select your device (MacBook/MacMini): ").lower()

# Assign file paths based on the user's choice (case insensitive)
if device_choice == "macbook":
    root_folder_path = "/Volumes/Cartella pubblica di Tommaso Prinetti/GENERATIONS"
    output_folder_path = "/Volumes/Cartella pubblica di Tommaso Prinetti/UPSCALED_IMAGES"
    logfile_path = "/Volumes/Cartella pubblica di Tommaso Prinetti/logfile_upscales.txt"
    metrics_file_path = "/Volumes/Cartella pubblica di Tommaso Prinetti/metrics.csv"
elif device_choice == "macmini":
    root_folder_path = "/Users/tommasoprinettim/Public/GENERATIONS"
    output_folder_path = "/Users/tommasoprinettim/Public/UPSCALED_IMAGES"
    logfile_path = "/Users/tommasoprinettim/Public/logfile_upscales.txt"
    metrics_file_path = "/Users/tommasoprinettim/Public/metrics.csv"
else:
    print("Invalid choice. Exiting...")
    exit()

# Function to encode image to base64
def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            image_content = image_file.read()
            base64_image = base64.b64encode(image_content).decode()
            return base64_image
    except FileNotFoundError:
        print("Error: Image file not found.")
        return None

# Create the output folder if it doesn't exist
os.makedirs(output_folder_path, exist_ok=True)

# Initialize tqdm progress bar
pbar = tqdm(desc="Processing Images")

# Initialize total_images count
total_images = 0

# Read processed filenames from the log file
processed_filenames = set()
if os.path.exists(logfile_path):
    with open(logfile_path, 'r') as logfile:
        processed_filenames.update(line.strip() for line in logfile.readlines()[1:])  # Skip the header

# Initialize metrics CSV file and write header if it doesn't exist
if not os.path.exists(metrics_file_path):
    with open(metrics_file_path, 'w', newline='') as metrics_file:
        writer = csv.writer(metrics_file)
        writer.writerow(["Filename", "RAM Usage (MB)", "CPU Usage (%)", "Time (s)"])
        print("Initializing metrics")

# Traverse the root folder and its subdirectories to count the total number of images
for root, dirs, files in os.walk(root_folder_path):
    for filename in files:
        if filename.endswith(".jpg") or filename.endswith(".png"):
            total_images += 1
            print("Root traversing, total images are:", total_images)

# Update total number of images in the progress bar
pbar.total = total_images

# Update the remaining time in the progress bar dynamically
with tqdm(total=total_images, desc="Processing Images") as pbar:
    for root, dirs, files in os.walk(root_folder_path):
        for filename in files:
            if filename.endswith(".jpg") or filename.endswith(".png"):
                # Check if the file has already been processed
                if filename in processed_filenames:
                    print(f"Skipping {filename}: Already processed")
                    pbar.update(1)
                    continue

                # Construct the full path of the image file
                image_path = os.path.join(root, filename)

                # Determine the relative path of the original image
                relative_path = os.path.relpath(root, root_folder_path)

                # Encode the image as base64
                base64_image = encode_image_to_base64(image_path)

                if base64_image:
                    try:
                        # Update the img2img_data with the base64 image
                        img2img_data["init_images"] = [base64_image]

                        # Measure start time
                        start_time = time.time()

                        # Monitor system resources before making the request
                        cpu_usage = psutil.cpu_percent()
                        ram_usage = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB

                        # Send a POST request to the Draw Things API with img2img_data
                        response_upscale = requests.post(url_img2img, json=img2img_data)

                        # Measure end time
                        end_time = time.time()

                        # Parse the JSON response
                        r = response_upscale.json()

                        # Print the response for debugging
                        #print("Response from API:", r)

                        # Loop through the images in the response
                        for idx, image_base64 in enumerate(r.get('images', [])):
                            # Decode the base64 image data
                            image_data = base64.b64decode(image_base64.split(",", 1)[0])

                            # Open the image using PIL
                            image = Image.open(io.BytesIO(image_data))

                            # Define the output filename
                            output_filename = os.path.splitext(filename)[0] + f"_upscaled_{idx+1}.png"

                            # Define the path to save the image with relative structure
                            relative_output_folder_path = os.path.join(output_folder_path, relative_path)
                            os.makedirs(relative_output_folder_path, exist_ok=True)
                            output_image_path = os.path.join(relative_output_folder_path, output_filename)

                            # Save the image as a PNG file
                            image.save(output_image_path)

                            # Print status message
                            print(f"Upscaled image saved as: {output_image_path}")

                            # Update progress bar
                            pbar.update(1)

                        # Calculate processing time
                        processing_time = end_time - start_time

                        # Write metrics to CSV file
                        with open(metrics_file_path, 'a', newline='') as metrics_file:
                            writer = csv.writer(metrics_file)
                            writer.writerow([filename, ram_usage, cpu_usage, processing_time])

                        pbar.set_postfix(Time=f"{processing_time:.2f}s")

                        # Add processed filename to the log file
                        with open(logfile_path, 'a') as logfile:
                            logfile.write(f"{filename}\n")

                    except requests.RequestException as e:
                        # Print an error message if there's an issue with the request
                        print(f"Error processing {filename}:", e)
            else:
                print(f"Skipping {filename}: Unsupported file format")
