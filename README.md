# Image Bank Project

This project is an image management system that processes, categorizes, and displays images based on their metadata. It includes features for extracting image metadata, organizing images into categories, and providing a web interface for browsing and searching the image collection.

## Features

- Metadata extraction from images using ExifTool
- Automatic categorization of images based on metadata
- Web interface for browsing and searching images
- Pagination for efficient navigation through large image collections
- Individual image view with download option
- Category view for exploring images by tags

## Testing Environment

The scripts in this project were tested with:
- Invoke AI UI
- Custom SDXL model

The captions, where the API is used, come from the Florence2 UI, which can be installed via Pinokio, similar to the Invoke AI UI installation process.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7+
- ExifTool installed on your system
- pip (Python package manager)
- Access to Invoke AI UI (for testing)
- Access to Florence2 UI via Pinokio (for captions)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/Alglior/automatic-image-bank
   cd automatic-image-bank
   ```

2. Install the required Python packages:
   ```
   pip install -r requirements.txt
   ```

3. Install ExifTool:
   - For MacOS (using Homebrew):
     ```
     brew install exiftool
     ```
   - For Ubuntu/Debian:
     ```
     sudo apt-get install libimage-exiftool-perl
     ```
   - For Windows:
     Download from the official website: https://exiftool.org/
     Add the ExifTool directory to your system PATH.

4. Set up Invoke AI UI and Florence2 UI:
   Follow the installation instructions for Invoke AI UI and Florence2 UI via Pinokio. These are required for testing and generating captions.

## Usage

1. Prepare your images:
   Place your images in the `input_images` folder.

2. Process the images:
   Run the main script to process and categorize the images:
   ```
   python main.py
   ```
   This will process the images in the `input_images` folder and organize them in the `output_folder`.

3. Initialize the image bank:
   Run the extraction script to create the image bank database:
   ```
   python extract.py
   ```
   This will create an `image_bank.json` file with the image metadata and categories.

4. Generate captions (optional):
   If you want to use AI-generated captions, ensure the Florence2 UI is running and use the `caption_florence2.py` script.

5. Start the web server:
   Run the Flask application:
   ```
   python images_bank_server.py
   ```
   The server will start, typically at `http://127.0.0.1:5000/`.

6. Access the web interface:
   Open a web browser and go to `http://127.0.0.1:5000/` to browse and search your image collection.

## Project Structure

- `main.py`: Processes images and extracts metadata
- `extract.py`: Initializes the image bank database
- `images_bank_server.py`: Flask server for the web interface
- `caption_florence2.py`: Script for generating image captions using Florence2 UI
- `input_images/`: Directory for input images
- `output_folder/`: Directory for processed and categorized images
- `captions.json`: JSON file containing image captions

## Contributing

Contributions to this project are welcome. Please follow these steps:

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Commit your changes (`git commit -m 'Add some amazing feature'`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a pull request

## License

This project is licensed under the MIT License - see the `LICENSE` file for details.

## Acknowledgements

- ExifTool for metadata extraction
- Flask for the web framework
- Gradio Client for AI-assisted image captioning
- Invoke AI UI for testing environment
- Florence2 UI (via Pinokio) for caption generation
