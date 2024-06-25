import os
import json
from flask import Flask, request, render_template_string, jsonify, send_from_directory

app = Flask(__name__)
database_file = 'image_bank.json'
image_root_folder = 'output_folder'  # The root folder containing categorized images
items_per_page = 50  # Number of items per page for pagination

# HTML template for the search interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Image Bank Search</title>
    <style>
        body {
            background-color: #1a1a40;
            color: #ffffff;
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center; /* Center content horizontally */
            min-height: 100vh;
            overflow-x: hidden;
        }
        header, footer {
            background-color: #0d0d26;
            padding: 10px;
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column; /* Arrange header items vertically */
        }
        .header-links {
            display: flex;
            justify-content: center;
            margin-top: 10px;
        }
        .header-link {
            margin: 0 10px;
            padding: 10px 20px;
            background-color: #ffd700;
            color: #1a1a40;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }
        .header-link:hover {
            background-color: #e0c600;
        }
        footer {
            bottom: 0;
            left: 0;
        }
        h1 {
            color: #ffd700;
            margin: 20px 0;
        }
        h1 a {
            color: #ffd700;
            text-decoration: none;
        }
        h1 a:hover {
            text-decoration: underline;
        }
        #results {
            margin-top: 20px;
            margin-right:5%;
            margin-left:5%;
            column-count: 7; /* Number of columns */
            column-gap: 2%; /* Gap between columns */
        }
        .image-container {
            margin-bottom: 20px;
            margin-right:10%;
            margin-left:10%;
            break-inside: avoid; /* Prevent container from breaking across columns */
            display: inline-block; /* Ensure inline block for proper layout */
            width: 100%; /* Full width for each container */
        }
        img {
            width: 100%; /* Image fills its container */
            border-radius: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            cursor: pointer;
            transition: transform 0.2s;
        }
        img:hover {
            transform: scale(1.05);
        }
        .pagination {
            display: flex;
            justify-content: center;
            margin: 20px;
        }
        .pagination button {
            padding: 10px 15px;
            margin: 5px;
            background-color: #ffd700;
            border: none;
            border-radius: 5px;
            color: #1a1a40;
            cursor: pointer;
        }
        .pagination button:hover {
            background-color: #e0c600;
        }

        .search-container {
            display: flex;
            justify-content: center;
            align-items: center;
            margin: 20px 0;
            flex-wrap: wrap;
        }
        input[type="text"] {
            width: 300px;
            padding: 10px;
            margin-right: 10px;
            margin-left: 20px;
            border: none;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        button {
            padding: 10px 20px;
            background-color: #ffd700;
            border: none;
            border-radius: 5px;
            color: #1a1a40;
            font-size: 16px;
            cursor: pointer;
            margin: 5px;
        }
        button:hover {
            background-color: #e0c600;
        }
    </style>
    <script>
        let currentPage = 1;
        const itemsPerPage = {{ items_per_page }};
        const maxPageButtons = 8;

        function searchImages(page = 1) {
            currentPage = page;
            const query = document.getElementById('searchBox').value.toLowerCase();
            fetch(`/search?q=${query}&page=${page}`)
                .then(response => response.json())
                .then(data => {
                    const resultsDiv = document.getElementById('results');
                    resultsDiv.innerHTML = '';
                    data.images.forEach(image => {
                        const imageContainer = document.createElement('div');
                        imageContainer.className = 'image-container';
                        const imgElement = document.createElement('img');
                        imgElement.src = 'output_folder/' + image.path;
                        imgElement.alt = image.tags.join(', ');
                        imgElement.onclick = () => { window.location.href = '/image/' + image.path };
                        imageContainer.appendChild(imgElement);
                        resultsDiv.appendChild(imageContainer);
                    });

                    updatePagination(data.total_pages, page);
                });
        }

        function updatePagination(totalPages, currentPage) {
            const paginationDivTop = document.getElementById('pagination-top');
            const paginationDivBottom = document.getElementById('pagination-bottom');
            paginationDivTop.innerHTML = '';
            paginationDivBottom.innerHTML = '';

            const createPageButton = (page, text = page) => {
                const pageButton = document.createElement('button');
                pageButton.textContent = text;
                pageButton.onclick = () => searchImages(page);
                if (page === currentPage) {
                    pageButton.style.fontWeight = 'bold';
                }
                return pageButton;
            };

            if (currentPage > 1) {
                paginationDivTop.appendChild(createPageButton(1, 'First'));
                paginationDivBottom.appendChild(createPageButton(1, 'First'));
            }

            const half = Math.floor(maxPageButtons / 2);
            let start = Math.max(currentPage - half, 1);
            let end = Math.min(start + maxPageButtons - 1, totalPages);

            if (end - start < maxPageButtons - 1) {
                start = Math.max(end - maxPageButtons + 1, 1);
            }

            for (let i = start; i <= end; i++) {
                const pageButtonTop = createPageButton(i);
                const pageButtonBottom = createPageButton(i);
                paginationDivTop.appendChild(pageButtonTop);
                paginationDivBottom.appendChild(pageButtonBottom);
            }

            if (currentPage < totalPages) {
                paginationDivTop.appendChild(createPageButton(totalPages, 'Last'));
                paginationDivBottom.appendChild(createPageButton(totalPages, 'Last'));
            }
        }

        window.onload = function() {
            searchImages();
            document.getElementById('searchBox').addEventListener('input', () => searchImages(1));
        }
    </script>
</head>
<body>
    <header>
        <h1>Image Bank</h1>
        <div class="search-container">
            <input type="text" id="searchBox" placeholder="Enter tags to search">
            <button onclick="searchImages()">Search</button>
            <button class="home-button" onclick="window.location.href='/categories'">View Categories</button>
        </div>
    </header>
    <div class="pagination" id="pagination-top"></div>
    <div id="results"></div>
    <div class="pagination" id="pagination-bottom"></div>
    <footer>
        <p>&copy; 2024 Image Bank. All rights reserved.</p>
    </footer>
</body>
</html>
"""


# HTML template for displaying the categories
CATEGORIES_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Categories</title>
    <style>
        body {
            background-color: #1a1a40;
            color: #ffffff;
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            overflow-x: hidden;
        }
        header, footer {
            background-color: #0d0d26;
            padding: 10px;
            width: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        footer {
            bottom: 0;
            left: 0;
        }
        .header-link {
            margin: 10px 0 0 0;
            padding: 10px 20px;
            background-color: #ffd700;
            color: #1a1a40;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }
        .header-link:hover {
            background-color: #e0c600;
        }
        h1 {
            color: #ffd700;
            margin: 20px 0;
        }
        .category-container {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-wrap: wrap;
            margin: 20px 0;
        }
        .category-button {
            position: relative;
            margin: 10px;
        }
        .category-button img {
            width: 200px;
            height: 200px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            cursor: pointer;
            transition: transform 0.2s;
        }
        .category-button img:hover {
            transform: scale(1.05);
        }
        .category-button span {
            position: absolute;
            bottom: 10px;
            left: 50%;
            transform: translateX(-50%);
            background-color: rgba(0, 0, 0, 0.5);
            color: white;
            padding: 5px 10px;
            border-radius: 5px;
        }
        .pagination {
            display: flex;
            justify-content: center;
            margin: 20px;
        }
        .pagination button {
            padding: 10px 15px;
            margin: 5px;
            background-color: #ffd700;
            border: none;
            border-radius: 5px;
            color: #1a1a40;
            cursor: pointer;
        }
        .pagination button:hover {
            background-color: #e0c600;
        }
    </style>
    <script>
        let currentPage = 1;
        const maxPageButtons = 5;  // Limit the number of pagination buttons visible

        function loadCategories(page = 1) {
            currentPage = page;
            fetch(`/categories_data?page=${page}`)
                .then(response => response.json())
                .then(data => {
                    const categoryContainer = document.querySelector('.category-container');
                    categoryContainer.innerHTML = '';
                    data.categories.forEach(category => {
                        const divElement = document.createElement('div');
                        divElement.className = 'category-button';
                        divElement.onclick = () => window.location.href = '/category/' + category.name;
                        
                        const imgElement = document.createElement('img');
                        imgElement.src = '../output_folder/' + category.image_path;
                        imgElement.alt = category.name;

                        const spanElement = document.createElement('span');
                        spanElement.textContent = category.name;

                        divElement.appendChild(imgElement);
                        divElement.appendChild(spanElement);
                        categoryContainer.appendChild(divElement);
                    });

                    updatePagination(data.total_pages, page);
                });
        }

        function updatePagination(totalPages, currentPage) {
            const paginationDivTop = document.querySelector('.pagination#pagination-top');
            const paginationDivBottom = document.querySelector('.pagination#pagination-bottom');
            paginationDivTop.innerHTML = '';
            paginationDivBottom.innerHTML = '';

            const createPageButton = (page, text = page) => {
                const pageButton = document.createElement('button');
                pageButton.textContent = text;
                pageButton.onclick = () => loadCategories(page);
                if (page === currentPage) {
                    pageButton.style.fontWeight = 'bold';
                }
                return pageButton;
            };

            // Add "First" button
            if (currentPage > 1) {
                paginationDivTop.appendChild(createPageButton(1, 'First'));
                paginationDivBottom.appendChild(createPageButton(1, 'First'));
            }

            // Determine the range of page buttons to show
            const half = Math.floor(maxPageButtons / 2);
            let start = Math.max(currentPage - half, 1);
            let end = Math.min(start + maxPageButtons - 1, totalPages);

            if (end - start < maxPageButtons - 1) {
                start = Math.max(end - maxPageButtons + 1, 1);
            }

            // Add page buttons
            for (let i = start; i <= end; i++) {
                const pageButtonTop = createPageButton(i);
                const pageButtonBottom = createPageButton(i);
                paginationDivTop.appendChild(pageButtonTop);
                paginationDivBottom.appendChild(pageButtonBottom);
            }

            // Add "Last" button
            if (currentPage < totalPages) {
                paginationDivTop.appendChild(createPageButton(totalPages, 'Last'));
                paginationDivBottom.appendChild(createPageButton(totalPages, 'Last'));
            }
        }

        window.onload = function() {
            loadCategories();  // Load categories on initial load
        }
    </script>
</head>
<body>
    <header>
        <h1>Image Bank</h1>
        <a href="/" class="header-link">Home</a>
    </header>
    <h1>Categories</h1>
    <div class="pagination" id="pagination-top"></div>
    <div class="category-container"></div>
    <div class="pagination" id="pagination-bottom"></div>
    <footer>
        <p>&copy; 2024 Image Bank. All rights reserved.</p>
    </footer>
</body>
</html>
"""

# HTML template for displaying an individual image
IMAGE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ tags }}</title>
    <style>
        body {
            background-color: #1a1a40;
            color: #ffffff;
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            overflow-x: hidden;
        }
        header, footer {
            background-color: #0d0d26;
            padding: 10px;
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column; /* Arrange header items vertically */
        }
        .header-links {
            display: flex;
            justify-content: center;
            margin-top: 10px;
        }
        .header-link {
            margin: 0 10px;
            padding: 10px 20px;
            background-color: #ffd700;
            color: #1a1a40;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }
        .header-link:hover {
            background-color: #e0c600;
        }
        footer {
            bottom: 0;
            left: 0;
        }
        h1 {
            color: #ffd700;
            margin-top: 20px;
        }
        h1 a {
            color: #ffd700;
            text-decoration: none;
        }
        h1 a:hover {
            text-decoration: underline;
        }
        img {
            margin: 20px auto;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            display: block; /* Ensure the image is displayed as a block element */
        }
        .download-button {
            margin-top: 20px;
            margin-bottom: 20px;
        }
        .download-button a {
            display: inline-block;
            padding: 10px 20px;
            background-color: #ffd700;
            color: #1a1a40;
            text-decoration: none;
            border-radius: 5px;
        }
        .download-button a:hover {
            background-color: #e0c600;
        }
    </style>
</head>
<body>
    <header>
        <h1>Image Bank</h1>
        <div class="header-links">
            <a href="javascript:history.back()" class="header-link">Back</a>
            <a href="/" class="header-link">Home</a>
        </div>
    </header>
    <h2>{{ title }}</h2>
    <h1>
    {% for tag in tags.split(', ') %}
        <a href="/category/{{ tag }}">{{ tag }}</a>{% if not loop.last %}, {% endif %}
    {% endfor %}
    </h1>
    
        
        

    
    <img src="../../output_folder/{{ path }}" alt="{{ tags }}">
    <p>{{ description }}</p>
    <div class="download-button">
        <a href="../../output_folder/{{ path }}" download>Download Image</a>
    </div>

    <footer>
        <p>&copy; 2024 Image Bank. All rights reserved.</p>
    </footer>
</body>
</html>
"""

# HTML template for displaying images in a category
CATEGORY_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{{ category }}</title>
        <p>{{ description }}</p>
    <style>
        body {
            background-color: #1a1a40;
            color: #ffffff;
            font-family: Arial, sans-serif;
            text-align: center;
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center; /* Center content horizontally */
            min-height: 100vh;
            overflow-x: hidden;
        }
        header, footer {
            background-color: #0d0d26;
            padding: 10px;
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column; /* Arrange header items vertically */
        }
        .header-links {
            display: flex;
            justify-content: center;
            margin-top: 10px;
        }
        .header-link {
            margin: 0 10px;
            padding: 10px 20px;
            background-color: #ffd700;
            color: #1a1a40;
            text-decoration: none;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }
        .header-link:hover {
            background-color: #e0c600;
        }
        footer {
            bottom: 0;
            left: 0;
        }
        h1 {
            color: #ffd700;
            margin: 20px 0;
        }
        h1 a {
            color: #ffd700;
            text-decoration: none;
        }
        h1 a:hover {
            text-decoration: underline;
        }
        #results {
            margin-top: 20px;
            margin-right:5%;
            margin-left:5%;
            column-count: 7; /* Number of columns */
            column-gap: 2%; /* Gap between columns */
        }
        .image-container {
            margin-bottom: 20px;
            break-inside: avoid; /* Prevent container from breaking across columns */
            display: inline-block; /* Ensure inline block for proper layout */
            width: 100%; /* Full width for each container */
        }
        img {
            width: 100%; /* Image fills its container */
            border-radius: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            cursor: pointer;
            transition: transform 0.2s;
        }
        img:hover {
            transform: scale(1.05);
        }
        .pagination {
            display: flex;
            justify-content: center;
            margin: 20px;
        }
        .pagination button {
            padding: 10px 15px;
            margin: 5px;
            background-color: #ffd700;
            border: none;
            border-radius: 5px;
            color: #1a1a40;
            cursor: pointer;
        }
        .pagination button:hover {
            background-color: #e0c600;
        }
    </style>
    <script>
        let currentPage = 1;
        const maxPageButtons = 5;  // Limit the number of pagination buttons visible

        function loadCategory(page = 1) {
            currentPage = page;
            fetch(`/category_data/{{ category }}?page=${page}`)
                .then(response => response.json())
                .then(data => {
                    const resultsDiv = document.getElementById('results');
                    resultsDiv.innerHTML = '';
                    data.images.forEach(image => {
                        const imageContainer = document.createElement('div');
                        imageContainer.className = 'image-container';
                        const imgElement = document.createElement('img');
                        imgElement.src = '../output_folder/' + image.path;
                        imgElement.alt = image.tags.join(', ');
                        imgElement.onclick = () => { window.location.href = '/image/' + image.path };
                        imageContainer.appendChild(imgElement);
                        resultsDiv.appendChild(imageContainer);
                    });

                    updatePagination(data.total_pages, page);
                });
        }

        function updatePagination(totalPages, currentPage) {
            const paginationDivTop = document.getElementById('pagination-top');
            const paginationDivBottom = document.getElementById('pagination-bottom');
            paginationDivTop.innerHTML = '';
            paginationDivBottom.innerHTML = '';

            const createPageButton = (page, text = page) => {
                const pageButton = document.createElement('button');
                pageButton.textContent = text;
                pageButton.onclick = () => loadCategory(page);
                if (page === currentPage) {
                    pageButton.style.fontWeight = 'bold';
                }
                return pageButton;
            };

            // Add "First" button
            if (currentPage > 1) {
                paginationDivTop.appendChild(createPageButton(1, 'First'));
                paginationDivBottom.appendChild(createPageButton(1, 'First'));
            }

            // Determine the range of page buttons to show
            const half = Math.floor(maxPageButtons / 2);
            let start = Math.max(currentPage - half, 1);
            let end = Math.min(start + maxPageButtons - 1, totalPages);

            if (end - start < maxPageButtons - 1) {
                start = Math.max(end - maxPageButtons + 1, 1);
            }

            // Add page buttons
            for (let i = start; i <= end; i++) {
                const pageButtonTop = createPageButton(i);
                const pageButtonBottom = createPageButton(i);
                paginationDivTop.appendChild(pageButtonTop);
                paginationDivBottom.appendChild(pageButtonBottom);
            }

            // Add "Last" button
            if (currentPage < totalPages) {
                paginationDivTop.appendChild(createPageButton(totalPages, 'Last'));
                paginationDivBottom.appendChild(createPageButton(totalPages, 'Last'));
            }
        }

        window.onload = function() {
            loadCategory();  // Load category images on initial load
        }
    </script>
</head>
<body>
    <header>
        <h1>Image Bank</h1>
        <div class="header-links">
            <a href="/categories" class="header-link">Back to Categories</a>
            <a href="/" class="header-link">Home</a>
        </div>
    </header>
    <h1>
    {% for word in category.split('_') %}
        <a href="/category/{{ word }}">{{ word }}</a>{% if not loop.last %} {% endif %}
    {% endfor %}
    </h1>

    <div class="pagination" id="pagination-top"></div>
    
    <div id="results"></div>
    <div class="pagination" id="pagination-bottom"></div>
    
    <footer>
        <p>&copy; 2024 Image Bank. All rights reserved.</p>
    </footer>
</body>
</html>

"""


def load_image_bank(database_file):
    if os.path.exists(database_file):
        with open(database_file, 'r') as f:
            data = json.load(f)
            return data['images'], data['categories']
    return {}, {}

def paginate_items(items, page, items_per_page):
    start = (page - 1) * items_per_page
    end = start + items_per_page
    return items[start:end], len(items)

@app.route('/')
def index():
    images, categories = load_image_bank(database_file)
    return render_template_string(HTML_TEMPLATE, categories=categories, items_per_page=items_per_page)

@app.route('/categories')
def categories():
    return render_template_string(CATEGORIES_TEMPLATE, items_per_page=items_per_page)

@app.route('/categories_data')
def categories_data():
    _, categories = load_image_bank(database_file)
    page = int(request.args.get('page', 1))
    category_list = [{'name': category, 'image_path': images[0]['path']} for category, images in categories.items()]
    
    paginated_categories, total_items = paginate_items(category_list, page, items_per_page)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    return jsonify({
        'categories': paginated_categories,
        'total_pages': total_pages
    })

@app.route('/search')
def search():
    query = request.args.get('q', '').lower()
    page = int(request.args.get('page', 1))
    print(f"Search query: {query}, Page: {page}")  # Debugging: print the search query
    results = []
    
    for folder, images in image_bank.items():
        for image in images:
            if any(query in tag.lower() for tag in image['tags']):
                results.append(image)
    
    paginated_results, total_items = paginate_items(results, page, items_per_page)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    return jsonify({
        'images': paginated_results,
        'total_pages': total_pages
    })

@app.route('/category/<category>')
def category(category):
    return render_template_string(CATEGORY_TEMPLATE, category=category)

@app.route('/category_data/<category>')
def category_data(category):
    _, categories = load_image_bank(database_file)
    page = int(request.args.get('page', 1))
    results = categories.get(category, [])
    
    paginated_results, total_items = paginate_items(results, page, items_per_page)
    total_pages = (total_items + items_per_page - 1) // items_per_page
    
    return jsonify({
        'images': paginated_results,
        'total_pages': total_pages
    })

@app.route('/output_folder/<path:filename>')
def serve_image(filename):
    return send_from_directory(image_root_folder, filename)

# Load captions from JSON file
def load_captions():
    with open('captions.json', 'r') as f:
        return json.load(f)

# Global variable to store captions
captions = load_captions()

@app.route('/image/<path:filename>')
def display_image(filename):
    # Find the image in the image bank
    image = next(
        (img for folder in image_bank.values() for img in folder if img['path'] == filename), None
    )
    if image:
        # Construct possible keys for the captions dictionary
        possible_keys = [
            filename,
            os.path.join('input_images', filename),
            filename.split('/')[-1],  # Just the filename without path
            os.path.join('input_images', filename.split('/')[-1])
        ]
        
        # Try to find the caption info using the possible keys
        caption_info = None
        for key in possible_keys:
            if key in captions:
                caption_info = captions[key]
                break
        
        # Print debug information
        print(f"Filename: {filename}")
        print(f"Caption info: {caption_info}")
        
        if caption_info:
            title = caption_info.get('title', 'No title available')
            description = caption_info.get('description', 'No description available')
        else:
            title = "No title available"
            description = "No description available"
        
        # Print more debug information
        print(f"Title: {title}")
        print(f"Description: {description}")
        
        return render_template_string(IMAGE_TEMPLATE, 
                                      path=filename, 
                                      tags=', '.join(image['tags']),
                                      title=title,
                                      description=description)
    else:
        return "Image not found", 404

# Debug route to view all captions
@app.route('/debug/captions')
def debug_captions():
    return json.dumps(captions, indent=2)

if __name__ == '__main__':
    # Load the image bank into memory
    image_bank, categories = load_image_bank(database_file)
    
    # Run the Flask app
    app.run(debug=True)