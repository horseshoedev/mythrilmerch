import React, { useState } from 'react';

function Header({ cartItemCount = 0 }) {
  const [searchQuery, setSearchQuery] = useState('');

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      // For now, just log the search query
      // In a real app, this would trigger a search API call
      console.log('Searching for:', searchQuery);
      alert(`Searching for: ${searchQuery} (Search functionality not implemented in demo)`);
    }
  };

  return (
    <header className="bg-primary-black text-button-text p-4 flex items-center justify-between">
      {/* Logo */}
      <div className="flex items-center">
        <div className="text-accent-red cursor-pointer mt-2">
          <h1 className="text-2xl font-logo">Mythril Merch</h1>
        </div>
      </div>

      {/* Search Bar */}
      <form onSubmit={handleSearch} className="flex-grow flex items-center bg-secondary-black hover:bg-gray-text rounded-md mx-4">
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="p-2 h-full flex-grow rounded-l-md focus:outline-none px-4 text-light-gray font-text"
          placeholder="Search products..."
          aria-label="Search products"
        />
        <button
          type="submit"
          className="h-full p-2 cursor-pointer text-light-gray hover:bg-hover-red rounded-r-md"
          aria-label="Search"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-6 w-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
            />
          </svg>
        </button>
      </form>

      {/* Right Section - Links */}
      <div className="flex items-center space-x-6 whitespace-nowrap">
        <div className="link font-text">
          <p className="text-xs">Hello, Sign In</p>
          <p className="font-bold text-sm">Accounts & Lists</p>
        </div>

        <div className="link font-text">
          <p className="text-xs">Returns</p>
          <p className="font-bold text-sm">& Orders</p>
        </div>

        <div className="link relative">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-10 w-10"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.182 1.769.704 1.769H19m-9 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z"
            />
          </svg>
          {cartItemCount > 0 && (
            <span className="absolute top-0 right-0 md:right-10 h-4 w-4 bg-accent-red text-center rounded-full text-button-text font-bold text-xs flex items-center justify-center font-text">
              {cartItemCount > 99 ? '99+' : cartItemCount}
            </span>
          )}
          <p className="hidden md:inline font-bold text-sm mt-2 font-text">Cart</p>
        </div>
      </div>
    </header>
  );
}

export default Header;