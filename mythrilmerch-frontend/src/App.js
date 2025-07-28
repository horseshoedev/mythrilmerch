import React, { useState, useEffect } from 'react';
//import Header from './components/Header';
import './App.css'; // Assuming you still have App.css, though Tailwind reduces its necessity


// Main App component
const App = () => {
  // State to store the list of products fetched from the backend
  const [products, setProducts] = useState([]);
  // State to manage items in the shopping cart (productId, quantity)
  const [cart, setCart] = useState([]);
  // State for displaying messages to the user (e.g., "Added to cart!")
  const [message, setMessage] = useState('');
  // Base URL for our Flask backend API
  const API_BASE_URL = '/.netlify/functions/api'; // Updated API_BASE_URL

  // useEffect hook to fetch products when the component mounts
  useEffect(() => {
    // Function to fetch products from the Flask backend
    const fetchProducts = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/products`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setProducts(data); // Update the products state with fetched data
      } catch (error) {
        console.error("Failed to fetch products:", error);
        setMessage("Failed to load products. Please check the backend server.");
      }
    };

    // Function to fetch cart items from the backend
    const fetchCartItems = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/cart`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        setCart(data); // Update the cart state with fetched data
      } catch (error) {
        console.error("Failed to fetch cart items:", error);
        setMessage("Failed to load cart. Please check the backend server.");
      }
    };


    fetchProducts(); // Call the fetch products function
    fetchCartItems(); // Call the fetch cart items function on mount as well
  }, []); // Empty dependency array means this runs once on mount

  // Function to add a product to the cart
  const addToCart = async (productId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/cart/add`, {
        method: 'POST', // Use POST method for adding data
        headers: {
          'Content-Type': 'application/json', // Specify content type as JSON
        },
        body: JSON.stringify({ productId: productId, quantity: 1 }), // Send product ID and quantity
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // No need to use the 'data' variable directly here if the backend doesn't return the full cart.
      // Instead, we will re-fetch the cart to ensure consistency with the database.
      // const data = await response.json(); // Original Line 49

      // Re-fetch cart to ensure consistency with database after adding an item
      const cartResponse = await fetch(`${API_BASE_URL}/cart`);
      if (!cartResponse.ok) {
          throw new Error(`HTTP error! status: ${cartResponse.status}`);
      }
      const updatedCartData = await cartResponse.json();
      setCart(updatedCartData); // Update cart state with the fresh data from the backend

      setMessage('Product added to cart!'); // Show success message
      // Clear message after a short delay
      setTimeout(() => setMessage(''), 2000);
    } catch (error) {
      console.error("Failed to add to cart:", error);
      setMessage("Failed to add product to cart.");
      setTimeout(() => setMessage(''), 3000);
    }
  };

  // Helper function to get full product details for cart display
  const getProductDetails = (productId) => {
    return products.find(product => product.id === productId);
  };

  // Calculate total price of items in the cart
  const calculateCartTotal = () => {
    return cart.reduce((total, item) => {
      const product = getProductDetails(item.productId);
      return total + (product ? product.price * item.quantity : 0);
    }, 0);
  };

  return (
    <div className="min-h-screen bg-gray-100 font-sans text-gray-800 p-4 sm:p-6 lg:p-8 rounded-lg shadow-lg">
      {/* Header */}
      {/* Header */}
      {/* Replace the custom header with the imported Header component */}
      <Header /> {/* This is the change */}

      <main className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Product List Section */}
        <section className="lg:col-span-2 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-6 text-gray-700">Products</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {products.length === 0 ? (
              <p className="col-span-full text-center text-gray-500">Loading products or no products available...</p>
            ) : (
              products.map((product) => (
                <ProductCard key={product.id} product={product} addToCart={addToCart} />
              ))
            )}
          </div>
        </section>

        {/* Shopping Cart Section */}
        <aside className="lg:col-span-1 bg-white p-6 rounded-lg shadow-md h-fit sticky top-8">
          <h2 className="text-2xl font-semibold mb-6 text-gray-700">Shopping Cart</h2>
          {cart.length === 0 ? (
            <p className="text-gray-500">Your cart is empty.</p>
          ) : (
            <>
              <ul>
                {cart.map((item) => {
                  // The cart items fetched from the backend will now include product details
                  // so we don't necessarily need getProductDetails here if the backend sends it all
                  // But keeping for consistency if backend structure changes or for simplicity if frontend wants to keep product details separate
                  const product = getProductDetails(item.productId);
                  return (
                    product && ( // Ensure product details are found before rendering
                      <li key={item.cartItemId} className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                        <div className="flex-1">
                          <p className="font-medium text-gray-900">{item.name}</p> {/* Use item.name from fetched cart */}
                          <p className="text-sm text-gray-600">Quantity: {item.quantity}</p>
                        </div>
                        <p className="font-semibold text-gray-800">${(item.price * item.quantity).toFixed(2)}</p> {/* Use item.price from fetched cart */}
                      </li>
                    )
                  );
                })}
              </ul>
              <div className="mt-6 pt-4 border-t-2 border-gray-300 flex justify-between items-center">
                <span className="text-lg font-bold text-gray-800">Total:</span>
                <span className="text-xl font-extrabold text-indigo-700">${calculateCartTotal().toFixed(2)}</span>
              </div>
              <button
                className="mt-6 w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-6 rounded-xl shadow-lg transition duration-300 ease-in-out transform hover:-translate-y-1"
                onClick={() => alert('Proceeding to checkout! (Not implemented in demo)')} // Simple alert for demo
              >
                Proceed to Checkout
              </button>
            </>
          )}
        </aside>
      </main>

      {/* Footer */}
      <footer className="mt-8 text-center text-gray-600 text-sm">
        <p>&copy; 2024 E-commerce Demo. All rights reserved.</p>
      </footer>
    </div>
  );
};

// ProductCard component for displaying individual product details
const ProductCard = ({ product, addToCart }) => {
  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-md overflow-hidden transition-transform duration-300 ease-in-out hover:scale-105 flex flex-col">
      <img
        src={product.imageUrl}
        alt={product.name}
        className="w-full h-48 object-cover object-center"
        onError={(e) => { e.target.onerror = null; e.target.src="https://placehold.co/150x150/CCCCCC/000000?text=No+Image"; }}
      />
      <div className="p-5 flex-grow flex flex-col justify-between">
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">{product.name}</h3>
          <p className="text-gray-600 text-sm mb-4 line-clamp-3">{product.description}</p>
        </div>
        <div className="flex justify-between items-center mt-auto pt-4 border-t border-gray-100">
          <span className="text-2xl font-bold text-indigo-600">${product.price.toFixed(2)}</span>
          <button
            onClick={() => addToCart(product.id)}
            className="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg shadow-md transition duration-300 ease-in-out transform hover:-translate-y-0.5"
          >
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;