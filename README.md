# EMIF-ImageGeneration
Private repository for the Stable Diffusion image generation pipeline.


# The guide
Here below you'll find a practical guide on how to access the python code responsible for the image generation Pipeline.

## Theorical background on Stable Diffusion

### Draw Things

For the whole generation pipeline we used Drawthings which is an ap for image generation widely used on arm64 Macs (since our machine were actually just M1 Pro macs).

Draw things is avery efficient compared to (let's guess) AUTOMATIC1111.

Theorically speaking our stable diffusion process worked like this.

We bake a prompt via txt2img generation using StableDiffusionXL vanilla as our based model.

[IMPORTANT] We forced ourselves in sing the base SDXL model as we needed to keep the results coherent with the LAION dataset. We indeed noticed that using checkpoints as base-models contributed heavily to biases in the generations, creating patterns of colors, object, subjects, etc.. that were not really consistent with the LAION dataset itself.  
 
Then we pass this img to the Stable Diffsion XL Official Refiner at 70% oif the generation. This step allows us to achieve way more details in the final image rather than just a one-shot base-model. Then, the image is passed again to the Hi-Res fix of SDXL. This passage is mainly intended to remove deformations in subjects and aberrations. Also, this step allows us to achieve way more details inside images and contributes to a generic image stabilization.

Having obtained a 1024x1024 image then we pass it to UltraSharp4x upscaler with a 200% upscale size to achieve a 2048x2048 image we could actively work on for printing purposes. 2048px correspond roughly to 4cm in a hypotethically 300dpi printing.

The we baked this image through a img2img process using a mixture of ControlNet, tiling mechanism and base img2img using JUGGERNAUT model variation of SDXL. In order to not lose the overall img, which is our main goal, the % of img2img generations was limited to 30%. This particular value allows us to intervene on the single objects of the generations, to restore their deformed shapes into photographic quality objects. The parameters used for the various ControlNet were tweaked from the original ones to achieve a more smooth and less crisp image.

The original script used for this step is called "Creative Upscale" and its user-generated, available directly on Drawthings. Especially, we extracted the various parameters used and implemented those in the python script we'll explain later.

The output of this process is a 2048x2048 image, highly photorealistic, loyal to the LAION dataset and SDXL generation mechanism.

## Theorical background of Draw Things platform

In order to generate our dataset of images (40*2*10 = 800) we had to find a way to automatize this process in both the txt2img step and the img2img step.

### The API

Draw Things relies on sdapi, but that's not really so much documentation on how to use it. In DT interface ("advanced") is possible to create a localhost with custom port to push JSON payloads and headlessly control the software.

Basically, it works like this:

#### Request method

We push a request to the localhost containing the json payload, which is a fixed 
template of variables that sdapi interpretes and applies to generate images.

The host answers mainly with a base64-encoded image. We then have to decode this image into a png, jpg or whatever: we chose png format.

The library used to make this request, is requests (how odd, isn't it?).

### The JSON payload

The JSON payload we send to the API is structred in two slighlty different ways based on the endpoint we are targetting.

if we target /img2img or /txt2img there are some variables that change. Luckily, the API is able to provide easy-to-debug prints were fed with non compatible variables in the payload.

[IMPORTANT] Generically in this project we'll refer to the payload as "api_data".

## The pipeline itself

For our purposes we structured the pipeline this way: [img]

The first script is responsible of generating the images, the second, to augment them as we explained in the beginning. Here below we show the 2 scripts that actually do this.

We'll take some lines to analyze each of them, in-depth:

# Generation

### We define the IP, PORT and URL of API:
`port = 7860
url = f"http://127.0.0.1:{port}"
endpoint = "/sdapi/v1/"

txt2img_url = f"{url}{endpoint}txt2img"`

### We define the location where we need the images to be saved.

`base_folder = "/GENERATIONS"`

### Ok this is specific for our nation variables:
We needed to create a queue of operations, to achieve automation:

`available_nations = sorted(set(variable['language'] for variable in variable_sets))

operation_queue = []`

`while True:
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

print("\nChosen operation queue:")
for idx, (nation, category, num_images) in enumerate(operation_queue, start=1):
    print(f"{idx}. Nation: {nation} - Category: {category} - Number of Images: {num_images}")`

Fundamentally, this initial part is for queue setupping.

### We store the img data into a csv to retain the base64 text encode
`csv_filename = "image_data.csv"
csv_path = os.path.join(base_folder, csv_filename)

csv_headers = ["Nation", "Category", "Base64 Code", "Filename", "CPU Usage (%)", "RAM Usage (MB)"]

with open(csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(csv_headers)`

### This is the actual generation pipeline. we firstly identify the correct prompt based on how the queue was formatted. Then we feed the prompt to the JSON payload.

    `# Iterate over the operation queue and generate images for each chosen combination
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
                os.makedirs(category_folder, exist_ok=True)`

## We also initialize some time in python to track how much time it's needed for the whole generation

                `# Initialize elapsed time
                total_elapsed_time = 0

                # Initialize list to store elapsed times for each image
                elapsed_times = []`

## Then we iterate the process, keeping an eye on the system resources, using psutil.

                `# Iterate for the specified number of images
                for i in tqdm(range(num_images), desc=f"Generating images for {chosen_nation} - {category}"):
                    try:
                        # Monitor system resources before making the request
                        cpu_usage = psutil.cpu_percent()
                        ram_usage = psutil.virtual_memory().used / (1024 * 1024)  # Convert to MB`

## This is the key point of our process. We send a POST request to the API and get the response which the we parse (it's a json).

                        `# Send a POST request to the Draw Things API with the updated parameters
                        response = requests.post(txt2img_url, json=txt2img_data)

                        # Parse the JSON response
                        r = response.json()`

## Having obtained the response we loop through the array of images contained in the json and decode each of them into a PNG image.

                        `# Loop through the images in the response
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
                            image.save(image_path)`

## This step is needed to track how much resources were used in each generation and in the overall process, to reverse obtain the amount of power involved.

                            `# Write image data and system monitoring data to the CSV file
                            writer.writerow([chosen_nation, category, image_base64, image_filename, cpu_usage, ram_usage])`

### PIL is used as corruption - checker in order to understand if the decoded IMG is healthy.
                            `try:
                                # Attempt to open the saved file with PIL to check for corruption
                                with Image.open(image_path) as img:
                                    # If the file opens successfully, print a message indicating that the image is not corrupted
                                    print(f"{BOLD}Image saved as {image_path}. Image is not corrupted.{RESET}")
                            except Exception as ex:
                                # If any exception occurs while opening the file, print a message indicating that the image might be corrupted
                                print(f"{BOLD}Image saved as {image_path}. Image might be corrupted: {ex}{RESET}")

                    except requests.RequestException as e:
                        # Print an error message if there's an issue with the request
                        print(f"{BOLD}Error: {e}{RESET}")`

### Finally, we continue the process
                        `# Continue to the next iteration if an error occurs
                        continue`

    



















