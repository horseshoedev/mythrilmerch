# Frontend Setup Guide

## Environment Configuration

Create a `.env` file in the `mythrilmerch-frontend` directory with the following content:

```env
# API Configuration
# Set this to your backend API URL
# For local development: http://localhost:5000
# For production: https://your-api-domain.com
REACT_APP_API_URL=http://localhost:5000

# Other environment variables can be added here
# REACT_APP_ENVIRONMENT=development
# REACT_APP_DEBUG=true
```

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

## Bug Fixes Implemented

### 1. **API URL Configuration**
- ✅ Replaced hardcoded localhost URL with environment variable
- ✅ Added fallback to localhost for development

### 2. **Loading States**
- ✅ Added loading spinners for products and cart
- ✅ Improved user experience during data fetching

### 3. **Error Handling**
- ✅ Added ErrorBoundary component for React errors
- ✅ Better error handling for missing products in cart
- ✅ Improved error messages and user feedback

### 4. **Cart Functionality**
- ✅ Fixed cart badge to show actual item count
- ✅ Added proper loading states for cart operations
- ✅ Prevented multiple simultaneous add-to-cart operations

### 5. **Accessibility**
- ✅ Added ARIA labels for better screen reader support
- ✅ Improved keyboard navigation
- ✅ Added proper form handling for search

### 6. **Memory Leaks**
- ✅ Fixed timeout cleanup to prevent memory leaks
- ✅ Used useCallback for stable function references

### 7. **Search Functionality**
- ✅ Added basic search form with validation
- ✅ Improved search input with proper event handling

### 8. **UI Improvements**
- ✅ Better loading indicators
- ✅ Disabled states for buttons during operations
- ✅ Improved error fallback images

## Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm eject` - Eject from Create React App (not recommended)

## Notes

- The search functionality currently shows an alert as it's not fully implemented
- The checkout button shows a demo alert
- All API calls use the configured `REACT_APP_API_URL` environment variable 