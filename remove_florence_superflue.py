import json

def process_captions(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)

    for image_info in data.values():
        if 'dense_region_caption' in image_info:
            # Remove 'bboxes' key and its content
            image_info['dense_region_caption'].pop('bboxes', None)
            
            # Filter out specific labels
            if 'labels' in image_info['dense_region_caption']:
                labels = image_info['dense_region_caption']['labels']
                image_info['dense_region_caption']['labels'] = [
                    label for label in labels 
                    if label not in ["human face", "human mouth"]
                ]

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)

# Usage
input_file = 'captions.json'
output_file = 'processed_captions.json'
process_captions(input_file, output_file)
print(f"Processed file saved as {output_file}")