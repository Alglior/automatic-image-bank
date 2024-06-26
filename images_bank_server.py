import os
import json
from flask import Flask, request,current_app,send_file,abort, render_template_string, jsonify, send_from_directory
from PIL import Image
import io
import logging
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
            flex-direction: column;
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
            display: block;
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
        .title {
            font-size: 2.5em;
            color: #ffd700;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
            margin: 30px 0;
            letter-spacing: 2px;
        }
        .description-box {
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            margin: 20px auto;
            max-width: 80%;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        .description-box p {
            margin: 0;
            line-height: 1.6;
        }
        .related-images {
            margin-top: 40px;
            padding: 20px;
            background-color: rgba(255, 255, 255, 0.05);
            border-radius: 10px;
        }
        .related-images h3 {
            color: #ffd700;
            margin-bottom: 20px;
        }
       .image-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            justify-items: center;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }
        .image-grid a {
            display: block;
            width: 100%;
            height: 0;
            padding-bottom: 100%; /* Creates a square aspect ratio */
            position: relative;
            overflow: hidden;
            border-radius: 10px; /* Rounded corners for the container */
            transition: transform 0.3s ease;
        }
        .image-grid img {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            border-radius: 10px; /* Rounded corners for the image */
            transition: transform 0.3s ease;
        }
        .image-grid a:hover {
            transform: scale(1.05);
            box-shadow: 0 0px 0px rgba(0, 0, 0, 0.2); /* Optional: adds a subtle shadow on hover */
        }
        .image-grid a:hover img {
            border-radius: 12px; /* Slightly larger radius on hover for a smooth effect */
        }
        @media (max-width: 480px) {
            .image-grid {
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            }
        }
        .image-container {
            display: flex;
            justify-content: center;
            align-items: flex-start;
            gap: 20px;
            margin: 20px auto;
            max-width: 1200px;
            padding: 0 20px;
        }
        .main-image-wrapper {
            flex: 1;
            max-width: 70%;
        }
        .main-image {
            width: 100%;
            height: auto;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        .image-info {
            flex: 0 0 25%;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            align-self: stretch;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .image-info h3 {
            color: #ffd700;
            margin-top: 0;
        }
        h3 {
            color: #ffd700;
            margin-top: 0;
        }
        .image-info p {
            margin: 10px 0;
        }
        @media (max-width: 768px) {
            .image-container {
                flex-direction: column;
                align-items: center;
            }
            .main-image-wrapper, .image-info {
                max-width: 100%;
                width: 100%;
            }
            .image-info {
                margin-top: 20px;
            }
        }
        .download-options {
            margin-top: 20px;
            margin-bottom: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .format-buttons {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 10px;
            margin-bottom: 15px;
        }
        .format-button {
            padding: 8px 15px;
            background-color: #2c2c6c;
            color: #ffffff;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        .format-button:hover, .format-button.selected {
            background-color: #ffd700;
            color: #1a1a40;
        }
        .download-button {
            display: inline-block;
            padding: 10px 20px;
            background-color: #ffd700;
            color: #1a1a40;
            text-decoration: none;
            border-radius: 5px;
            font-size: 16px;
            transition: background-color 0.3s ease;
        }
        .download-button:hover {
            background-color: #e0c600;
        }
    </style>
    </div>
    <script>
        document.querySelectorAll('.format-button').forEach(button => {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const downloadUrl = this.href;
                
                fetch(downloadUrl)
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`HTTP error! status: ${response.status}`);
                        }
                        return response.blob();
                    })
                    .then(blob => {
                        const url = window.URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.style.display = 'none';
                        a.href = url;
                        // Extract the format from the button's text
                        const format = this.textContent.split(' ')[1].toLowerCase();
                        a.download = `{{ path.split('/')[-1].split('.')[0] }}.${format}`;
                        document.body.appendChild(a);
                        a.click();
                        window.URL.revokeObjectURL(url);
                    })
                    .catch(e => {
                        console.error('Download failed:', e);
                        alert(`Download failed: ${e.message}`);
                    });
            });
        });
    </script>
</head>
<body>
    <header>
        <h1>Image Bank</h1>
        <div class="header-links">
            <a href="javascript:history.back()" class="header-link">Back</a>
            <a href="/" class="header-link">Home</a>
        </div>
    </header>
    <h2 class="title">{{ title }}</h2>
    <h1>
        {% for tag in tags.split(', ') %}
        <a href="/category/{{ tag }}">{{ tag }}</a>{% if not loop.last %}, {% endif %}
        {% endfor %}
    </h1>
       <div class="image-container">
        <img class="main-image" src="../../output_folder/{{ path }}" alt="{{ tags }}">
        <div class="image-info">
            <h3>Image Information</h3>
            <p><strong>Type:</strong> {{ img_type }}</p>
            <p><strong>Dimensions:</strong> {{ img_size }}</p>
            <p><strong>File Size:</strong> {{ file_size }}</p>
        </div>
    </div>
    <div class="description-box">
        <p>{{ description }}</p>
    </div>
    <h3>Download Section</h3>
    <div class="download-options">
    
        <div class="format-buttons">
            {% for format in ['JPEG', 'PNG', 'TIFF', 'BMP', 'WEBP', 'GIF'] %}
                <a href="/download/{{ path }}/{{ format }}" class="format-button" download>Download {{ format }}</a>
            {% endfor %}
        </div>
    </div>
    <div class="related-images">
        <h3>Related Images</h3>
        <div class="image-grid">
            {% for image in related_images %}
            <a href="{{ image.url }}">
                <img src="{{ image.thumbnail }}" alt="{{ image.tags }}">
            </a>
            {% endfor %}
        </div>
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
        (img for folder in image_bank.values() for img in folder if img['path'] == filename),
        None
    )
    
    if not image:
        abort(404, description="Image not found")

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
    
    # Get title and description
    title = caption_info.get('title', 'No title available') if caption_info else "No title available"
    description = caption_info.get('description', 'No description available') if caption_info else "No description available"
    
    # Get image type, dimensions, and file size
    img_path = os.path.join('output_folder', filename)
    try:
        with Image.open(img_path) as img:
            original_format = img.format
            img_type = original_format
            img_size = f"{img.width}x{img.height}"
            file_size = os.path.getsize(img_path)
            file_size_mb = f"{file_size / (1024 * 1024):.2f} MB"
            
            # Prepare available formats
            available_formats = ['JPEG', 'PNG', 'TIFF', 'BMP']
            if original_format not in available_formats:
                available_formats.append(original_format)
    except IOError:
        img_type = "Unknown"
        img_size = "Unknown"
        file_size_mb = "Unknown"
        available_formats = []

    # Find related images (images with the same first tag)
    related_images = []
    if image['tags']:
        first_tag = image['tags'][0]
        for folder in image_bank.values():
            for img in folder:
                if img['path'] != filename and first_tag in img['tags']:
                    related_images.append({
                        "url": f"/image/{img['path']}",
                        "thumbnail": f"../../output_folder/{img['path']}",
                        "tags": ', '.join(img['tags'])
                    })
                    if len(related_images) >= 8:  # Limit to 8 related images
                        break
            if len(related_images) >= 8:
                break

    return render_template_string(IMAGE_TEMPLATE,
                                  path=filename,
                                  tags=', '.join(image['tags']),
                                  title=title,
                                  description=description,
                                  related_images=related_images,
                                  img_type=img_type,
                                  img_size=img_size,
                                  file_size=file_size_mb,
                                  available_formats=available_formats)

@app.route('/download/<path:filename>/<format>')
def download_image(filename, format):
    try:
        logging.info(f"Attempting to download image: {filename} in format: {format}")

        img_path = os.path.join(current_app.root_path, 'output_folder', filename)
        logging.info(f"Full image path: {img_path}")

        if not os.path.exists(img_path):
            logging.error(f"Image file not found: {img_path}")
            abort(404, description="Image file not found")

        logging.info(f"Image file found: {img_path}")

        with Image.open(img_path) as img:
            byte_io = io.BytesIO()
            
            if format.upper() in ['JPEG', 'JPG']:
                if img.mode in ['RGBA', 'LA']:
                    img = img.convert('RGB')
                img.save(byte_io, format='JPEG', quality=95)
            elif format.upper() == 'PNG':
                img.save(byte_io, format='PNG')
            elif format.upper() == 'TIFF':
                img.save(byte_io, format='TIFF')
            elif format.upper() == 'BMP':
                img.save(byte_io, format='BMP')
            elif format.upper() == 'WEBP':
                img.save(byte_io, format='WEBP')
            elif format.upper() == 'GIF':
                img.save(byte_io, format='GIF')
            else:
                logging.error(f"Unsupported format: {format}")
                abort(400, description="Unsupported image format")
            
            byte_io.seek(0)
            
            download_name = f"{os.path.splitext(filename)[0]}.{format.lower()}"
            
            logging.info(f"Sending file: {download_name}")
            return send_file(
                byte_io,
                as_attachment=True,
                download_name=download_name,
                mimetype=f'image/{format.lower()}'
            )

    except Exception as e:
        logging.error(f"Error during download of {filename} in {format} format: {str(e)}")
        abort(500, description=f"Server error during download: {str(e)}")

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Debug route to view all captions
@app.route('/debug/captions')
def debug_captions():
    return json.dumps(captions, indent=2)

if __name__ == '__main__':
    # Load the image bank into memory
    image_bank, categories = load_image_bank(database_file)
    
    # Run the Flask app
    app.run(debug=True)