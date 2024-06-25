import json
import requests
import subprocess,os

def check_ollama_status():
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        print("Ollama status:")
        print(result.stdout)
        return True
    except FileNotFoundError:
        print("Ollama command not found. Please make sure Ollama is installed and in your PATH.")
        return False

def modify_text_with_ollama(text):
    url = "http://localhost:11434/api/generate"  # Correct Ollama API endpoint
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": "llama3",  # Llama 3 small model
        "prompt": f"""
        Human: Please modify the following text according to these rules:
        1. Replace "horse" with "centaur woman"
        2. Try to stay as close as possible to the original text
        3. Keep the same syntax and presentation

        Text to modify: "{text}"

        Assistant: Here's the modified text:
        """,
        "stream": False,
        "nsfw": True  # Enable NSFW content handling
    }

    
    try:
        print(f"Sending request to: {url}")
        print(f"Request data: {json.dumps(data, indent=2)}")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Response status code: {response.status_code}")
        print(f"Response content: {response.text}")
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()["response"].strip()
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to modify text. {e}")
        if hasattr(e, 'response'):
            print(f"Response content: {e.response.content}")
        return None

def modify_json_file(input_file, output_file):
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Check if output_file exists, load modified entries if it does
    if os.path.exists(output_file):
        with open(output_file, 'r') as out_f:
            modified_data = json.load(out_f)
    else:
        modified_data = {}

    for key, entry in data.items():
        if key not in modified_data:
            modified_entry = {}
            if "title" in entry:
                modified_title = entry["title"].replace("woman and horse", "centaur woman")
                modified_title = modify_text_with_ollama(modified_title)
                modified_entry["title"] = modified_title

            if "description" in entry:
                modified_description = entry["description"].replace("woman and horse", "centaur woman")
                modified_description = modify_text_with_ollama(modified_description)
                modified_entry["description"] = modified_description

            # Add id and name_image directly from input data
            modified_entry["id"] = entry["id"]
            modified_entry["name_image"] = entry["name_image"]

            # Store the modified entry immediately
            modified_data[key] = modified_entry

            # Save modified entry to output file after each modification
            with open(output_file, 'w') as out_f:
                json.dump(modified_data, out_f, indent=4)
                print(f"Entry with key '{key}' modified and saved to '{output_file}'")
        else:
            print(f"Entry with key '{key}' already exists in '{output_file}'. Skipping...")

    print(f"Modification complete. Modified JSON saved to {output_file}")


# Function to execute another Python script
def execute_another_script(script_path):
    subprocess.run(['python3', script_path])

if __name__ == "__main__":
    input_json_file = "../captions.json"  # Replace with your input JSON file path
    output_json_file = "../modified_output.json"  # Replace with desired output JSON file path
    
    if not check_ollama_status():
        print("Ollama doesn't seem to be running or installed. Please check your Ollama installation.")
    else:
        # Test the Ollama connection before processing the file
        print("Testing Ollama connection...")
        test_result = modify_text_with_ollama("This is a test sentence with a woman and horse.")
        if test_result:
            print("Ollama connection successful. Proceeding with file modification.")
            modify_json_file(input_json_file, output_json_file)
            print(f"Modification complete. Modified JSON saved to {output_json_file}")
            
            # Execute another script after completion
            print("Executing another script...")
            execute_another_script("remove_text_secondary.py")
            
            print("All tasks completed.")
        else:
            print("Failed to connect to Ollama. Please check your setup and try again.")
