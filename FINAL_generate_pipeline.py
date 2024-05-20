import requests
import os
import base64
import time
import io
import csv
import psutil 
from PIL import Image
from tqdm import tqdm
from api_parameters_txt2img import txt2img_data
from variable_set import variable_sets

# Define the URL of the API endpoint
port = 7860
url = f"http://127.0.0.1:{port}"
endpoint = "/sdapi/v1/"

txt2img_url = f"{url}{endpoint}txt2img"
png_info_url = f"{url}{endpoint}png-info"

# Define the base folder where you want to save the generated images
base_folder = "/Volumes/Cartella pubblica di Tommaso Prinetti/GENERATIONS"

#/Volumes/Cartella pubblica di Tommaso Prinetti/GENERATIONS #macbook

#/Users/tommasoprinettim/Public/GENERATIONS #macmini

# List all available nations
available_nations = sorted(set(variable['language'] for variable in variable_sets))

# Initialize the queue of operations
operation_queue = []

while True:
    print("Available nations:")
    for i, nation in enumerate(available_nations, start=1):
        print(f"{i}. {nation}")
    nation_input = input("Enter the number corresponding to the nation you want to choose (or 'done' to start image generation): ")

    if nation_input.lower() == 'done':
        break
    elif nation_input.isdigit():
        nation_choice = int(nation_input) - 1
        if 0 <= nation_choice < len(available_nations):
            chosen_nation = available_nations[nation_choice]
            # Prompt user to choose between family or workers
            category = input("Enter 'family' or 'working' to choose the category: ")
            # Prompt user to enter the number of images to generate
            num_images = int(input("Enter the number of images to generate: "))
            # Add the chosen nation, category, and number of images to the operation queue
            operation_queue.append((chosen_nation, category, num_images))
        else:
            print("Please enter a number between 1 and", len(available_nations))
    else:
        print("Invalid input. Please enter a number or 'done' to start image generation.")

# Print the chosen operation queue
print("\nChosen operation queue:")
for idx, (nation, category, num_images) in enumerate(operation_queue, start=1):
    print(f"{idx}. Nation: {nation} - Category: {category} - Number of Images: {num_images}")

# ANSI escape codes for formatting text
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RESET = '\033[0m'

# Create a CSV file to store image data
csv_filename = "image_data.csv"
csv_path = os.path.join(base_folder, csv_filename)

# Define CSV column headers
csv_headers = ["Nation", "Category", "Base64 Code", "Filename", "CPU Usage (%)", "RAM Usage (MB)"]

# Open the CSV file in write mode and write headers
with open(csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(csv_headers)

    # Iterate over the operation queue and generate images for each chosen combination
    for idx, (chosen_nation, category, num_images) in enumerate(operation_queue, start=1):
        # Filter variable_sets based on user input
        filtered_variable_sets = [variables for variables in variable_sets if variables["language"].lower() == chosen_nation.lower() and category.lower() in variables["prompt_addition"].lower()]

        # Check if any matching variable sets were found
        if not filtered_variable_sets:
            print(f"{BOLD}No matching variables found for {chosen_nation} - {category}{RESET}")
        else:
            for variables in filtered_variable_sets:
                # Construct the prompt with the current set of variables
                prompt = f"{variables['prompt_addition']}, (35mm lens photography), extremely detailed, 4k, shot on dslr, photorealistic, photographic, sharp"

                # Construct the dictionary containing the parameters
                txt2img_data["prompt"] = prompt

                # Define the folder path for the current nation and category
                nation_folder = os.path.join(base_folder, chosen_nation)
                category_folder = os.path.join(nation_folder, category)

                # Create the nested folders if they don't exist
                os.makedirs(category_folder, exist_ok=True)

                # Initialize elapsed time
                total_elapsed_time = 0

                # Initialize list to store elapsed times for each image
                elapsed_times = []

                # Iterate for the specified number of images
                for i in tqdm(range(num_images), desc=f"Generating images for {chosen_nation} - {category}"):
                    try:
                        # Monitor system resources before making the request
                        cpu_usage = psutil.cpu_percent()
                        ram_usage = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB

                        # Send a POST request to the Draw Things API with the updated parameters
                        response = requests.post(txt2img_url, json=txt2img_data)

                        # Parse the JSON response
                        r = response.json()

                        # Loop through the images in the response
                        for idx, image_base64 in enumerate(r['images']):
                            # Decode the base64 image data
                            image_data = base64.b64decode(image_base64.split(",", 1)[0])

                            # Open the image using PIL
                            image = Image.open(io.BytesIO(image_data))

                            # Define the filename for the image
                            image_filename = f"{chosen_nation}_{category}_{i+1}_{idx+1}.png"

                            # Define the path to save the image
                            image_path = os.path.join(category_folder, image_filename)

                            # Save the image as a PNG file
                            image.save(image_path)

                            # Write image data and system monitoring data to the CSV file
                            writer.writerow([chosen_nation, category, image_base64, image_filename, cpu_usage, ram_usage])

                            try:
                                # Attempt to open the saved file with PIL to check for corruption
                                with Image.open(image_path) as img:
                                    # If the file opens successfully, print a message indicating that the image is not corrupted
                                    print(f"{BOLD}Image saved as {image_path}. Image is not corrupted.{RESET}")
                            except Exception as ex:
                                # If any exception occurs while opening the file, print a message indicating that the image might be corrupted
                                print(f"{BOLD}Image saved as {image_path}. Image might be corrupted: {ex}{RESET}")

                    except requests.RequestException as e:
                        # Print an error message if there's an issue with the request
                        print(f"{BOLD}Error: {e}{RESET}")

                        # Continue to the next iteration if an error occurs
                        continue
