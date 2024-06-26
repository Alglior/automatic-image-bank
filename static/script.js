let currentPage = 1;
const itemsPerPage = 100; // This should match the server-side value
const maxPageButtons = 5;

function searchImages(page = 1, scrollToTop = false) {
    currentPage = page;
    const query = document.getElementById('searchBox').value.toLowerCase();
    const endpoint = query ? `/search?q=${query}&page=${page}` : `/latest-images?page=${page}`;
    
    fetch(endpoint)
        .then(response => response.json())
        .then(data => {
            updateResults(data.images);
            updatePagination(data.total_pages, page, searchImages);

            if (scrollToTop) {
                window.scrollTo({top: 0, behavior: 'smooth'});
            }
        });
}

function loadCategory(page = 1, scrollToTop = false) {
    currentPage = page;
    const category = document.body.getAttribute('data-category');
    fetch(`/category_data/${category}?page=${page}`)
        .then(response => response.json())
        .then(data => {
            updateResults(data.images);
            updatePagination(data.total_pages, page, loadCategory);

            if (scrollToTop) {
                window.scrollTo({top: 0, behavior: 'smooth'});
            }
        });
}

function updateResults(images) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';
    images.forEach(image => {
        const imageContainer = document.createElement('div');
        imageContainer.className = 'image-container';
        
        const imgElement = document.createElement('img');
        imgElement.src = '../output_folder/' + image.path;
        imgElement.alt = image.tags.join(', ');
        imageContainer.appendChild(imgElement);
        
        const infoDiv = document.createElement('div');
        infoDiv.className = 'image-info';
        infoDiv.innerHTML = `
            <h3>${image.title || 'No title'}</h3>
            <p>${image.tags.slice(0, 3).join(', ')}</p>
        `;
        imageContainer.appendChild(infoDiv);
        
        imageContainer.onclick = () => { window.location.href = '/image/' + image.path };
        resultsDiv.appendChild(imageContainer);
    });
}

function updatePagination(totalPages, currentPage, loadFunction) {
    const paginationDivTop = document.getElementById('pagination-top');
    const paginationDivBottom = document.getElementById('pagination-bottom');
    paginationDivTop.innerHTML = '';
    paginationDivBottom.innerHTML = '';

    const createPageButton = (page, text = page, isBottom = false) => {
        const pageButton = document.createElement('button');
        pageButton.textContent = text;
        pageButton.onclick = () => loadFunction(page, isBottom);
        if (page === currentPage) {
            pageButton.style.fontWeight = 'bold';
        }
        return pageButton;
    };

    if (currentPage > 1) {
        paginationDivTop.appendChild(createPageButton(1, 'First'));
        paginationDivBottom.appendChild(createPageButton(1, 'First', true));
    }

    const half = Math.floor(maxPageButtons / 2);
    let start = Math.max(currentPage - half, 1);
    let end = Math.min(start + maxPageButtons - 1, totalPages);

    if (end - start < maxPageButtons - 1) {
        start = Math.max(end - maxPageButtons + 1, 1);
    }

    for (let i = start; i <= end; i++) {
        paginationDivTop.appendChild(createPageButton(i));
        paginationDivBottom.appendChild(createPageButton(i, i, true));
    }

    if (currentPage < totalPages) {
        paginationDivTop.appendChild(createPageButton(totalPages, 'Last'));
        paginationDivBottom.appendChild(createPageButton(totalPages, 'Last', true));
    }
}

function initializeDownloadButtons() {
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
                    const filename = this.getAttribute('data-filename') || 'image';
                    a.download = `${filename}.${format}`;
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
}

window.onload = function() {
    const category = document.body.getAttribute('data-category');
    if (category) {
        loadCategory(); // Load category images on initial load
    } else if (document.querySelector('.format-button')) {
        initializeDownloadButtons(); // Initialize download buttons for individual image page
    } else {
        searchImages(); // Load latest images on initial load for main page
        document.getElementById('searchBox').addEventListener('input', () => searchImages(1));
        document.getElementById('stickySearchBox').addEventListener('input', () => {
            document.getElementById('searchBox').value = document.getElementById('stickySearchBox').value;
            searchImages(1);
        });

        window.addEventListener('scroll', function() {
            var header = document.querySelector('header');
            var sticky = document.querySelector('.sticky-search');
            if (window.pageYOffset > header.offsetTop + header.offsetHeight) {
                sticky.style.display = 'block';
            } else {
                sticky.style.display = 'none';
            }
        });
    }
}