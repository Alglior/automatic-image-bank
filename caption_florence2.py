import os
import json
from gradio_client import Client, handle_file
import ast

def parse_caption(caption_string):
    try:
        caption_dict = ast.literal_eval(caption_string)
        return list(caption_dict.values())[0]
    except:
        return caption_string.strip()

def caption_image(client, image_path, id_number):
    try:
        regular_caption_result = client.predict(
            image=handle_file(image_path),
            task_prompt="Caption",
            text_input=None,
            model_id="microsoft/Florence-2-large",
            api_name="/process_image"
        )
        regular_caption = parse_caption(regular_caption_result[0])

        detailed_caption_result = client.predict(
            image=handle_file(image_path),
            task_prompt="More Detailed Caption",
            text_input=None,
            model_id="microsoft/Florence-2-large",
            api_name="/process_image"
        )
        detailed_caption = parse_caption(detailed_caption_result[0])

        title = os.path.splitext(os.path.basename(image_path))[0]
        return {
            "id": str(id_number),
            "name_image": f"{id_number}_{title}",
            "title": regular_caption,
            "description": detailed_caption
        }
    except Exception as e:
        print(f"Error processing {image_path}: {str(e)}")
        return None

def process_folder(folder_path):
    client = Client("http://127.0.0.1:7860/")
    captions_data = {}
    json_path = os.path.join(folder_path, '../captions.json')
    
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            captions_data = json.load(f)
    
    id_counter = len(captions_data) + 1  # Start ID from the next available number

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            image_path = os.path.join(folder_path, filename)
            if image_path in captions_data:
                print(f"Caption already exists for {filename}, skipping.")
                continue
            
            image_data = caption_image(client, image_path, id_counter)
            if image_data:
                captions_data[image_path] = image_data
                print(f"Processed {filename} with ID {id_counter}")
                id_counter += 1

                with open(json_path, 'w') as f:
                    json.dump(captions_data, f, indent=4)
            else:
                print(f"Failed to generate caption for {filename}")

    print(f"All captions saved to {json_path}")

# Usage
folder_path = 'input_images'
process_folder(folder_path)