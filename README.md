# EMIF-ImageGeneration
Private repository for the Stable Diffusion image generation pipeline.
---

## The Guide
Below you'll find a practical guide on how to access the Python code responsible for the image generation pipeline.

## Theoretical Background on Stable Diffusion

### Draw Things

For the whole generation pipeline, we used **[Draw Things](https://drawthings.ai/)**, an app for image generation widely used on ```ARM64 Macs``` (since our machines were M1 Pro Macs).
Draw Things is very efficient compared to (let's guess) AUTOMATIC1111. 🎨

Theoretically speaking, our stable diffusion process worked like this:

We applied a prompt via `txt2img` generation using the [Stable Diffusion XL official model](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0) as our base model.

> **IMPORTANT**: We forced ourselves to use the base SDXL model to keep the results coherent with the LAION dataset. We noticed that using checkpoints as base models contributed heavily to biases in the generations, creating patterns of colors, objects, subjects, etc., that were not consistent with the LAION dataset itself.

Then we pass this image to the **Stable Diffusion XL Official Refiner** at ```70%``` of the generation. This step allows us to achieve way more details in the final image rather than just a one-shot base model. Then, the image is passed again to the ```Hi-Res fix of SDXL```. This passage is mainly intended to remove deformations in subjects and aberrations. Also, this step allows us to achieve way more details inside images and contributes to generic image stabilization. 🔄

Having obtained a `1024x1024` image, we then pass it to **UltraSharp4x upscaler** with a `200%` upscale size to achieve a `2048x2048` image we could actively work on for printing purposes. 2048px corresponds roughly to 4cm in a hypothetical 300dpi printing. 🖨️

Then we bake this image through an `img2img` process using a mixture of **ControlNet**, tiling mechanism, and base `img2img` using the **[JUGGERNAUT model variation of SDXL](https://civitai.com/models/133005/juggernaut-xl)**.

In order to not "lose" the overall image, which is our main goal, the percentage of `img2img` generations was limited to `30%`. This particular value allows us to intervene on the single objects of the generations, to restore their deformed shapes into photographic quality objects. The parameters used for the various `ControlNet` were tweaked from the original ones to achieve a smoother and less crisp image.

The original script used for this step is called "Creative Upscale" and is user-generated, available directly on Draw Things. Especially, we extracted the various parameters used and implemented those in the Python script we'll explain later.

The output of this process is a `2048x2048` image, highly photorealistic, loyal to the LAION dataset and SDXL generation mechanism.

## Theoretical Background of Draw Things Platform

In order to generate our dataset of images `(40*2*10 = 800)`, we had to find a way to automate this process in both the `txt2img` step and the `img2img` step.

### The API

Draw Things relies on `sdapi`, but there's not much documentation on how to use it. In the DT interface ("advanced"), it's possible to create a localhost with a custom port to push JSON payloads and headlessly control the software.

Basically, it works like this:

#### Request Method

We push a request to the localhost containing the JSON payload, which is a fixed template of variables that `sdapi` interprets and applies to generate images.

The host answers mainly with a base64-encoded image. We then have to decode this image into a PNG, JPG, or whatever format we choose: we chose PNG format.

The library used to make this request is "requests" (how odd).

```python
response = requests.post(endpoint, json=payload)
r = response.json()
```

### The JSON Payload

The JSON payload we send to the API is structured in two slightly different ways based on the endpoint we are targeting.

If we target `/img2img` or `/txt2img`, there are some variables that change. Luckily, the API is able to provide easy-to-debug prints when fed with non-compatible variables in the payload.

> **IMPORTANT**: Generally, in this project, we'll refer to the payload as "api_data".

You can find the complete `sdapi` payload in the file named: `api_payload list`.

## The pipeline itself

For our purposes, we structured the pipeline this way: [img]

The first script is responsible of generating the images, the second, to augment them as we explained in the beginning. Here below we show the 2 scripts that actually do this.

We'll take some lines to analyze each of them, in-depth:

---

# Generation

### We define the IP, PORT and URL of API:

```python
port = 7860
url = f"http://127.0.0.1:{port}"
endpoint = "/sdapi/v1/"

txt2img_url = f"{url}{endpoint}txt2img"
```

### We define the location where we need the images to be saved.

```python
base_folder = "/GENERATIONS"
```

### Ok this is specific for our nation variables:
We needed to create a queue of operations, to achieve automation:

```python
available_nations = sorted(set(variable['language'] for variable in variable_sets))

operation_queue = []
```

```python
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
            
            category = input("Enter 'family' or 'working' to choose the category: ")

            num_images = int(input("Enter the number of images to generate: "))

            operation_queue.append((chosen_nation, category, num_images))
        else:
            print("Please enter a number between 1 and", len(available_nations))
    else:
        print("Invalid input. Please enter a number or 'done' to start image generation.")

print("\nChosen operation queue:")
for idx, (nation, category, num_images) in enumerate(operation_queue, start=1):
    print(f"{idx}. Nation: {nation} - Category: {category} - Number of Images: {num_images}")
```

Fundamentally, this initial part is for queue setup.

### We store the img data into a CSV to retain the base64 text encode

```python
csv_filename = "image_data.csv"
csv_path = os.path.join(base_folder, csv_filename)

csv_headers = ["Nation", "Category", "Base64 Code", "Filename", "CPU Usage (%)", "RAM Usage (MB)"]

with open(csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(csv_headers)
```

### This is the actual generation pipeline. We firstly identify the correct prompt based on how the queue was formatted. Then we feed the prompt to the JSON payload.

```python

for idx, (chosen_nation, category, num_images) in enumerate(operation_queue, start=1):
    
    filtered_variable_sets = [variables for variables in variable_sets if variables["language"].lower() == chosen_nation.lower() and category.lower() in variables["prompt_addition"].lower()]

    if not filtered_variable_sets:
        print(f"{BOLD}No matching variables found for {chosen_nation} - {category}{RESET}")
    else:
        for variables in filtered_variable_sets:
           
            prompt = f"{variables['prompt_addition']}, (35mm lens photography), extremely detailed, 4k, shot on dslr, photorealistic, photographic, sharp"

            txt2img_data["prompt"] = prompt

            nation_folder = os.path.join(base_folder, chosen_nation)
            category_folder = os.path.join(nation_folder, category)

            os.makedirs(category_folder, exist_ok=True)
```

### We also initialize some time in Python to track how much time it's needed for the whole generation.

```python
            total_elapsed_time = 0

            elapsed_times = []
```

### Then we iterate the process, keeping an eye on the system resources, using `psutil`.

```python
            for i in tqdm(range(num_images), desc=f"Generating images for {chosen_nation} - {category}"):
                try:
                    cpu_usage = psutil.cpu_percent()
                    ram_usage = psutil.virtual_memory().used / (1024 * 1024)
```

### This is the key point of our process. We send a POST request to the API and get the response which we then parse (it's a JSON).

```python
                    response = requests.post(txt2img_url, json=txt2img_data)

                    r = response.json()
```

### Having obtained the response, we loop through the array of images contained in the JSON and decode each of them into a PNG image.

```python
for idx, image_base64 in enumerate(r['images']):
    
    image_data = base64.b64decode(image_base64.split(",", 1)[0])

    image = Image.open(io.BytesIO(image_data))

    image_filename = f"{chosen_nation}_{category}_{i+1}_{idx+1}.png"

    image_path = os.path.join(category_folder, image_filename)

    image.save(image_path)
```

### This step is needed to track how much resources were used in each generation and in the overall process, to reverse obtain the amount of power involved.

```python              
        writer.writerow([chosen_nation, category, image_base64, image_filename, cpu_usage, ram_usage])
```

### PIL is used as a corruption-checker to understand if the decoded image is healthy.

```python
        try:
            
            with Image.open(image_path) as img:
                
                print(f"{BOLD}Image saved as {image_path}. Image is not corrupted.{RESET}")
        except Exception as ex:
            
            print(f"{BOLD}Image saved as {image_path}. Image might be corrupted: {ex}{RESET}")

except requests.RequestException as e:
   
    print(f"{BOLD}Error: {e}{RESET}")
```

### Finally, we continue the process.

```python
        continue
```

---

# Upscaling

### As before, we define the API endpoint:

```url_img2img = "http://127.0.0.1:7860/sdapi/v1/img2img"```

### Since our upscaling process ran simltaneosly on two macbooks, that get their images from different folders as we were sharing one on a local server, the first step is make the user choose the correct working device. 
```python

device_choice = input("Select your device (MacBook/MacMini): ").lower()

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
```

### This time we are loading an existent image for the img2img process, this can be done using the ```init_images``` parameter inside the json payload. This parameter supports an array of base64 images that loads as the base for the generation.

```python

def encode_image_to_base64(image_path):
    try:
        with open(image_path, "rb") as image_file:
            image_content = image_file.read()
            base64_image = base64.b64encode(image_content).decode()
            return base64_image
    except FileNotFoundError:
        print("Error: Image file not found.")
        return None

os.makedirs(output_folder_path, exist_ok=True)

pbar = tqdm(desc="Processing Images")

total_images = 0
```

### Here we logged the processed filenames so that we were able to track the yet-processed ones and not throw away time.

```python

processed_filenames = set()
if os.path.exists(logfile_path):
    with open(logfile_path, 'r') as logfile:
        processed_filenames.update(line.strip() for line in logfile.readlines()[1:])
```

### As before, we keep track of the system metrics involved in this process
```python

if not os.path.exists(metrics_file_path):
    with open(metrics_file_path, 'w', newline='') as metrics_file:
        writer = csv.writer(metrics_file)
        writer.writerow(["Filename", "RAM Usage (MB)", "CPU Usage (%)", "Time (s)"])
        print("Initializing metrics")
```

### Then we need the script to firstly understand dinamically how much images are left in the folder, so that when running the same script on two machines at ones we avoid false data:
```python

for root, dirs, files in os.walk(root_folder_path):
    for filename in files:
        if filename.endswith(".jpg") or filename.endswith(".png"):
            total_images += 1
            print("Root traversing, total images are:", total_images)

pbar.total = total_images

with tqdm(total=total_images, desc="Processing Images") as pbar:
    for root, dirs, files in os.walk(root_folder_path):
        for filename in files:
            if filename.endswith(".jpg") or filename.endswith(".png"):
                # Check if the file has already been processed
                if filename in processed_filenames:
                    print(f"Skipping {filename}: Already processed")
                    pbar.update(1)
                    continue

                image_path = os.path.join(root, filename)

                relative_path = os.path.relpath(root, root_folder_path)
```
### After having identified the img to process, we proceed encoding it into base64 and feeding it to the img2img_data:
```python

                base64_image = encode_image_to_base64(image_path)

                if base64_image:
                    try:
                        img2img_data["init_images"] = [base64_image]

                        start_time = time.time()

                        cpu_usage = psutil.cpu_percent()
                        ram_usage = psutil.virtual_memory().used / (1024 * 1024)

                        response_upscale = requests.post(url_img2img, json=img2img_data)

                        end_time = time.time()

                        r = response_upscale.json()
                        
                        for idx, image_base64 in enumerate(r.get('images', [])):
                            
                            image_data = base64.b64decode(image_base64.split(",", 1)[0])

                            
                            image = Image.open(io.BytesIO(image_data))

                            
                            output_filename = os.path.splitext(filename)[0] + f"_upscaled_{idx+1}.png"

                            
                            relative_output_folder_path = os.path.join(output_folder_path, relative_path)
                            os.makedirs(relative_output_folder_path, exist_ok=True)
                            output_image_path = os.path.join(relative_output_folder_path, output_filename)

                            
                            image.save(output_image_path)

                            print(f"Upscaled image saved as: {output_image_path}")
```
### After having collected the result image we update the TQDM which is tracking the process, update the CSV and the log file:
``` python

                            pbar.update(1)

                        processing_time = end_time - start_time

                        with open(metrics_file_path, 'a', newline='') as metrics_file:
                            writer = csv.writer(metrics_file)
                            writer.writerow([filename, ram_usage, cpu_usage, processing_time])

                        pbar.set_postfix(Time=f"{processing_time:.2f}s")

                        with open(logfile_path, 'a') as logfile:
                            logfile.write(f"{filename}\n")

                    except requests.RequestException as e:
                        
                        print(f"Error processing {filename}:", e)
            else:
                print(f"Skipping {filename}: Unsupported file format")
```
### Then we just move over to the next unprocessed img.

The output of the entire pipeline is a folder of 2048x2048 images, highly photorealistic.
The structure of the output is:

```
GENERATION
|-Nation
    |--Workers
    |--Family
```
# Image segmentation

We need then to proceed with img-segmenetation to divide the various objects of the images.
To automate this process we used the SegmentAnything library of META AI, tweaked and adapted to work with our structured data. We won't go deep on how this thing works but it works, with a definetly high precision.

The output of this script is a folder strctured the same way sa before but with pieces of images, each in 1:1 png with the same location as before, cut-outed from everything else.





