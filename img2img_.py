import requests
from tqdm import tqdm
from PIL import Image
import io
import base64

# Define the URL of the API endpoint for img2img
url = "http://127.0.0.1:7860/sdapi/v1/img2img"

def pil_to_base64(pil_image):
    with io.BytesIO() as stream:
        pil_image.save(stream, "jpeg")  # Save the image as JPEG format
        base64_str = base64.b64encode(stream.getvalue()).decode('utf-8')
        return "data:image/jpeg;base64," + base64_str  # Change the MIME type to 'image/jpeg'

# Path to the folder containing images
images_folder = "/Users/tommasoprinetti/Documents/TIROCINIO/STEREOTYPES/TEST" 

# List all image files in the folder
image_files = ["TEST.jpeg"] 

# Iterate over each image file, load it, and send it to the API
for image_file in image_files:
    try:
        # Construct the full path of the image file
        image_path = f"{images_folder}/{image_file}"

        # Debug print: Check the path of the image being processed
        print(f"Processing image: {image_path}")

        # Load the image
        image = Image.open(image_path)

        # Debug print: Check if the image is loaded successfully
        print("Image loaded successfully.")

        # Convert the PIL image to base64
        base64_image = pil_to_base64(image)

        # Define the payload for API request
        payload = {
            "init_images": [base64_image]
        }

        # Send a POST request to the img2img API endpoint with the payload
        with tqdm(total=1, desc="Sending request to API") as pbar:  # Initialize tqdm progress bar
            response = requests.post(url=url, json=payload)
            pbar.update(1)  # Update progress bar when request is sent

        # Debug print: Check if the request was sent successfully
        print("Request sent to API successfully.", response)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Print a message indicating that the image generation process is complete
            print("🔥 Image generation process complete.")
        else:
            # Print an error message if the request was unsuccessful
            print(f"Error: {response.status_code}")
    except FileNotFoundError:
        # Print an error message if the file is not found
        print(f"File {image_file} not found.")
    except Exception as e:
        # Print an error message if there's an issue processing the image
        print(f"Error processing {image_file}: {e}")
