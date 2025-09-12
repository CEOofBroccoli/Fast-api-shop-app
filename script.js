document.addEventListener('DOMContentLoaded', () => {
    const productsContainer = document.getElementById('products-container');

    async function fetchProducts() {
        try {
            const response = await fetch('http://localhost:8000/products', {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                }
            });
            const products = await response.json();

            if (response.ok) {
                displayProducts(products);
            } else {
                console.error('Failed to fetch products:', products.detail);
                productsContainer.innerHTML = '<p>Failed to load products.</p>';
            }
        } catch (error) {
            console.error('Error fetching products:', error);
            productsContainer.innerHTML = '<p>Error loading products.</p>';
        }
    }

    function displayProducts(products) {
        productsContainer.innerHTML = ''; // Clear existing content
        products.forEach(product => {
            const productCard = document.createElement('div');
            productCard.className = 'col-sm-12 col-md-6 col-lg-3';
            productCard.innerHTML = `
                <div class="card" style="width: 18rem;">
                    <img src="./assets/images/47.jpg" class="card-img-top" alt="...">
                    <div class="card-body">
                        <h5 class="card-title">${product.name}</h5>
                        <p class="card-text">${product.description || 'No description available'}</p>
                        <p class="card-text">Price: $${product.price}</p>
                        <a href="#" class="btn btn-primary">خریداری محصول</a>
                    </div>
                </div>
            `;
            productsContainer.appendChild(productCard);
        });
    }

    // Check if the user is logged in and has a token
    const token = localStorage.getItem('access_token');
    if (token) {
        fetchProducts();
    } else {
        productsContainer.innerHTML = '<p>Please log in to view products.</p>';
    }
});