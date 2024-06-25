import json
import re

def remove_modified_text(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for key in data:
        # Check and update 'description' if necessary
        if 'description' in data[key]:
            description = data[key]['description']
            if description.startswith("Here is the modified text:"):
                new_description = description.replace("Here is the modified text:", "").strip()
                data[key]['description'] = new_description
        
        # Check and update 'title' if necessary
        if 'title' in data[key]:
            title = data[key]['title']
            if title.startswith("Here is the modified text:"):
                new_title = title.replace("Here is the modified text:", "").strip()
                data[key]['title'] = new_title
        
        # Check and update 'name_image' if necessary
        if 'name_image' in data[key]:
            name_image = data[key]['name_image']
            # Use regular expression to remove number before '_' and the '_'
            new_name_image = re.sub(r'\d+_', '', name_image)
            data[key]['name_image'] = new_name_image
    
    # Write the updated data back to the JSON file
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# Example usage:
json_file = '../modified_output.json'  # Replace with your actual JSON file path
remove_modified_text(json_file)
print(f"Modified JSON saved to {json_file}")
