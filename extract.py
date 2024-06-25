import json, os, re, subprocess

def extract_metadata(image_path):
    try:
        result = subprocess.run(['exiftool', image_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Error extracting metadata from {image_path}: {result.stderr}")
    except Exception as e:
        print(f"Error running exiftool on {image_path}: {e}")
    return None

def sanitize_folder_name(name):
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def extract_metadata_info(metadata):
    """Extract the full positive prompt from the metadata."""
    info = {'positive_prompt': None}
    for line in metadata.split('\n'):
        for key in info.keys():
            if f'"{key}":' in line:
                try:
                    start_index = line.index(f'"{key}":"') + len(f'"{key}":"')
                    end_index = line.index('",', start_index)
                    info[key] = line[start_index:end_index].strip()
                    print(f"Extracted {key}: {info[key]}")
                except (ValueError, IndexError) as e:
                    print(f"Error parsing '{key}' from metadata: {e}")
    return info

def initialize_image_bank(image_root_folder, database_file='image_bank.json'):
    image_bank = {}
    categories = {}
    
    for root, _, files in os.walk(image_root_folder):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
                folder_name = os.path.basename(root)
                metadata = extract_metadata(os.path.join(root, file))
                metadata_info = extract_metadata_info(metadata) if metadata else {}
                positive_prompt = metadata_info.get('positive_prompt', None)
                tags = [tag.strip() for tag in positive_prompt.split(',')] if positive_prompt else folder_name.split('_')
                
                print(f"Image: {file}, Tags: {tags}")
                
                image_path = os.path.join(root, file)
                image_info = {
                    "path": os.path.relpath(image_path, image_root_folder),
                    "tags": tags
                }
                
                for tag in tags:
                    if tag:
                        if tag not in categories:
                            categories[tag] = []
                        categories[tag].append(image_info)

                if folder_name not in image_bank:
                    image_bank[folder_name] = []
                
                image_bank[folder_name].append(image_info)
    
    with open(database_file, 'w') as f:
        json.dump({'images': image_bank, 'categories': categories}, f)
    print(f"Image bank initialized and saved to {database_file}")

initialize_image_bank('output_folder')