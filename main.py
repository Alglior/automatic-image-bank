import os
import shutil
import subprocess
import re

def extract_metadata(image_path):
    """Extract metadata from an image using exiftool."""
    try:
        result = subprocess.run(['exiftool', image_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode == 0:
            return result.stdout
        else:
            print(f"Error extracting metadata from {image_path}: {result.stderr}")
    except Exception as e:
        print(f"Error running exiftool on {image_path}: {e}")
    return None

def save_metadata_to_file(metadata, file_path):
    """Save metadata to a text file."""
    try:
        with open(file_path, 'w') as f:
            f.write(metadata)
        print(f"Metadata saved to {file_path}")
    except Exception as e:
        print(f"Error saving metadata to {file_path}: {e}")

def sanitize_folder_name(name):
    """Sanitize the folder name by removing or replacing invalid characters."""
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def extract_positive_prompt(metadata):
    """Extract the full positive prompt from the metadata."""
    positive_prompt = None
    for line in metadata.split('\n'):
        if '"positive_prompt":' in line:
            try:
                start_index = line.index('"positive_prompt":"') + len('"positive_prompt":"')
                end_index = line.index('",', start_index)
                positive_prompt = line[start_index:end_index].strip()
                print(f"Extracted positive prompt: {positive_prompt}")
                return positive_prompt
            except (ValueError, IndexError) as e:
                print(f"Error parsing 'positive_prompt' from metadata: {e}")
    return None

def process_images(input_folder, output_folder):
    """Process each image in the input folder."""
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp', '.gif')):
            image_path = os.path.join(input_folder, filename)
            print(f"Processing {image_path}")
            metadata = extract_metadata(image_path)
            
            if metadata:
                base_name = os.path.splitext(filename)[0]
                positive_prompt = extract_positive_prompt(metadata)
                
                if positive_prompt:
                    new_dir_name = sanitize_folder_name(positive_prompt)
                    print(f"Positive prompt found: {positive_prompt}")
                else:
                    new_dir_name = base_name
                    print(f"No 'positive_prompt' found. Using base name: {base_name}")

                new_dir = os.path.join(output_folder, new_dir_name)
                
                if not os.path.exists(new_dir):
                    os.makedirs(new_dir)
                    print(f"Created directory: {new_dir}")
                
                new_image_path = os.path.join(new_dir, filename)
                metadata_file_path = os.path.join(new_dir, f"{base_name}_metadata.txt")
                
                shutil.copy2(image_path, new_image_path)
                print(f"Copied image to {new_image_path}")
                save_metadata_to_file(metadata, metadata_file_path)
            else:
                print(f"No metadata found for {filename}")


# Example usage
input_folder = 'input_images'
output_folder = 'output_folder'
process_images(input_folder, output_folder)
