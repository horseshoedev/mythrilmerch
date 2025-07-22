import React from 'react';

function Header() {
  return (
    <header className="bg-amazon_blue text-white p-4 flex items-center justify-between">
      {/* Logo */}
      <div className="flex items-center">
        <img
          src="https://pngimg.com/uploads/amazon/amazon_PNG11.png" // Amazon logo
          alt="Amazon Logo"
          className="w-24 cursor-pointer mt-2"
        />
      </div>

      {/* Search Bar */}
      <div className="flex-grow flex items-center bg-yellow-400 hover:bg-yellow-500 rounded-md mx-4">
        <input
          type="text"
          className="p-2 h-full flex-grow rounded-l-md focus:outline-none px-4 text-black"
          placeholder="Search Amazon"
        />
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-10 w-10 p-2 cursor-pointer text-gray-800"
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
      </div>

      {/* Right Section - Links */}
      <div className="flex items-center space-x-6 whitespace-nowrap">
        <div className="link">
          <p className="text-xs">Hello, Sign In</p>
          <p className="font-bold text-sm">Accounts & Lists</p>
        </div>

        <div className="link">
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
          <span className="absolute top-0 right-0 md:right-10 h-4 w-4 bg-yellow-400 text-center rounded-full text-black font-bold">
            0
          </span>
          <p className="hidden md:inline font-bold text-sm mt-2">Cart</p>
        </div>
      </div>
    </header>
  );
}

export default Header;