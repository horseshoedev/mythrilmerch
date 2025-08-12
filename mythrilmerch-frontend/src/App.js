import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import './App.css';

// Main App component
const App = () => {
  // State to store the list of products fetched from the backend
  const [products, setProducts] = useState([]);
  // State to manage items in the shopping cart (productId, quantity)
  const [cart, setCart] = useState([]);
  // State for displaying messages to the user (e.g., "Added to cart!")
  const [message, setMessage] = useState('');
  // Loading states
  const [isLoadingProducts, setIsLoadingProducts] = useState(true);
  const [isLoadingCart, setIsLoadingCart] = useState(true);
  const [isAddingToCart, setIsAddingToCart] = useState(false);
  // Base URL for our Flask backend API - use environment variable with fallback
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

  // Function to fetch products from the Flask backend
  const fetchProducts = useCallback(async () => {
    try {
      setIsLoadingProducts(true);
      const response = await fetch(`${API_BASE_URL}/products`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setProducts(data);
    } catch (error) {
      console.error("Failed to fetch products:", error);
      setMessage("Failed to load products. Please check the backend server.");
    } finally {
      setIsLoadingProducts(false);
    }
  }, [API_BASE_URL]);

  // Function to fetch cart items from the backend
  const fetchCartItems = useCallback(async () => {
    try {
      setIsLoadingCart(true);
      const response = await fetch(`${API_BASE_URL}/cart`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setCart(data);
    } catch (error) {
      console.error("Failed to fetch cart items:", error);
      setMessage("Failed to load cart. Please check the backend server.");
    } finally {
      setIsLoadingCart(false);
    }
  }, [API_BASE_URL]);

  // useEffect hook to fetch products when the component mounts
  useEffect(() => {
    fetchProducts();
    fetchCartItems();
  }, [fetchProducts, fetchCartItems]);

  // Function to add a product to the cart
  const addToCart = async (productId) => {
    try {
      setIsAddingToCart(true);
      const response = await fetch(`${API_BASE_URL}/cart/add`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ productId: productId, quantity: 1 }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // Re-fetch cart to ensure consistency with database after adding an item
      await fetchCartItems();

      setMessage('Product added to cart!');
      // Clear message after a short delay
      const timeoutId = setTimeout(() => setMessage(''), 2000);
      return () => clearTimeout(timeoutId);
    } catch (error) {
      console.error("Failed to add to cart:", error);
      setMessage("Failed to add product to cart.");
      const timeoutId = setTimeout(() => setMessage(''), 3000);
      return () => clearTimeout(timeoutId);
    } finally {
      setIsAddingToCart(false);
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

  // Calculate total number of items in cart
  const getCartItemCount = () => {
    return cart.reduce((total, item) => total + item.quantity, 0);
  };

  return (
    <div className="min-h-screen bg-gray-100 font-text text-gray-800">
      <Header cartItemCount={getCartItemCount()} />
      <div className="p-4 sm:p-6 lg:p-8 rounded-lg shadow-lg">

      {/* Message Display */}
      {message && (
        <div className="mb-4 p-4 bg-blue-100 border border-blue-400 text-blue-700 rounded-lg font-text" role="alert">
          {message}
        </div>
      )}

      <main className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Product List Section */}
        <section className="lg:col-span-2 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-6 text-gray-700 font-logo">Products</h2>
          {isLoadingProducts ? (
            <div className="flex justify-center items-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              <span className="ml-2 text-gray-600 font-text">Loading products...</span>
            </div>
          ) : products.length === 0 ? (
            <p className="text-center text-gray-500 py-8 font-text">No products available.</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
              {products.map((product) => (
                <ProductCard 
                  key={product.id} 
                  product={product} 
                  addToCart={addToCart}
                  isAddingToCart={isAddingToCart}
                />
              ))}
            </div>
          )}
        </section>

        {/* Shopping Cart Section */}
        <aside className="lg:col-span-1 bg-white p-6 rounded-lg shadow-md h-fit sticky top-8">
          <h2 className="text-2xl font-semibold mb-6 text-gray-700 font-logo">Shopping Cart</h2>
          {isLoadingCart ? (
            <div className="flex justify-center items-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
              <span className="ml-2 text-gray-600 font-text">Loading cart...</span>
            </div>
          ) : cart.length === 0 ? (
            <p className="text-gray-500 font-text">Your cart is empty.</p>
          ) : (
            <>
              <ul>
                {cart.map((item) => {
                  const product = getProductDetails(item.productId);
                  if (!product) {
                    return (
                      <li key={item.cartItemId} className="py-2 border-b border-gray-200 last:border-b-0">
                        <p className="text-red-600 text-sm font-text">Product no longer available</p>
                      </li>
                    );
                  }
                  return (
                    <li key={item.cartItemId} className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                      <div className="flex-1">
                        <p className="font-medium text-gray-900 font-text">{product.name}</p>
                        <p className="text-sm text-gray-600 font-text">Quantity: {item.quantity}</p>
                      </div>
                      <p className="font-semibold text-gray-800 font-text">${(product.price * item.quantity).toFixed(2)}</p>
                    </li>
                  );
                })}
              </ul>
              <div className="mt-6 pt-4 border-t-2 border-gray-300 flex justify-between items-center">
                <span className="text-lg font-bold text-gray-800 font-text">Total:</span>
                <span className="text-xl font-extrabold text-indigo-700 font-text">${calculateCartTotal().toFixed(2)}</span>
              </div>
              <button
                className="mt-6 w-full bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-3 px-6 rounded-xl shadow-lg transition duration-300 ease-in-out transform hover:-translate-y-1 disabled:opacity-50 disabled:cursor-not-allowed font-text"
                onClick={() => alert('Proceeding to checkout! (Not implemented in demo)')}
                disabled={cart.length === 0}
                aria-label="Proceed to checkout"
              >
                Proceed to Checkout
              </button>
            </>
          )}
        </aside>
      </main>

      {/* Footer */}
      <footer className="mt-8 text-center text-gray-600 text-sm font-text">
        <p>&copy; Mythril Merch {new Date().getFullYear()}. All rights reserved.</p>
      </footer>
      </div>
    </div>
  );
};

// ProductCard component for displaying individual product details
const ProductCard = ({ product, addToCart, isAddingToCart }) => {
  const handleAddToCart = () => {
    if (!isAddingToCart) {
      addToCart(product.id);
    }
  };

  return (
    <div className="bg-white border border-gray-200 rounded-xl shadow-md overflow-hidden transition-transform duration-300 ease-in-out hover:scale-105 flex flex-col">
      <img
        src={product.imageUrl}
        alt={product.name}
        className="w-full h-48 object-cover object-center"
        onError={(e) => { 
          e.target.onerror = null; 
          e.target.src="https://via.placeholder.com/300x200/CCCCCC/666666?text=No+Image"; 
        }}
      />
      <div className="p-5 flex-grow flex flex-col justify-between">
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2 font-logo">{product.name}</h3>
          <p className="text-gray-600 text-sm mb-4 line-clamp-3 font-text">{product.description}</p>
        </div>
        <div className="flex justify-between items-center mt-auto pt-4 border-t border-gray-100">
          <span className="text-2xl font-bold text-indigo-600 font-text">${product.price.toFixed(2)}</span>
          <button
            onClick={handleAddToCart}
            disabled={isAddingToCart}
            className="bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white font-semibold py-2 px-4 rounded-lg shadow-md transition duration-300 ease-in-out transform hover:-translate-y-0.5 disabled:cursor-not-allowed font-text"
            aria-label={`Add ${product.name} to cart`}
          >
            {isAddingToCart ? 'Adding...' : 'Add to Cart'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default App;