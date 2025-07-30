# MythrilMerch Database Schema

This directory contains the database schema and setup files for the MythrilMerch e-commerce application.

## Schema Overview

The database consists of the following tables:

### Core Tables

1. **`products`** - Product catalog
   - `id` (SERIAL PRIMARY KEY)
   - `name` (VARCHAR(255)) - Product name
   - `description` (TEXT) - Product description
   - `price` (DECIMAL(10,2)) - Product price
   - `image_url` (VARCHAR(500)) - Product image URL
   - `created_at` (TIMESTAMP) - Creation timestamp
   - `updated_at` (TIMESTAMP) - Last update timestamp

2. **`cart_items`** - Shopping cart items
   - `id` (SERIAL PRIMARY KEY)
   - `product_id` (INTEGER) - Foreign key to products
   - `quantity` (INTEGER) - Item quantity
   - `created_at` (TIMESTAMP) - Creation timestamp
   - `updated_at` (TIMESTAMP) - Last update timestamp

### Future Tables (for upcoming features)

3. **`users`** - User accounts (for authentication)
   - `id` (SERIAL PRIMARY KEY)
   - `email` (VARCHAR(255) UNIQUE) - User email
   - `name` (VARCHAR(255)) - User name
   - `created_at` (TIMESTAMP) - Creation timestamp
   - `updated_at` (TIMESTAMP) - Last update timestamp

4. **`orders`** - Order management
   - `id` (SERIAL PRIMARY KEY)
   - `user_id` (INTEGER) - Foreign key to users
   - `total_amount` (DECIMAL(10,2)) - Order total
   - `status` (VARCHAR(50)) - Order status
   - `created_at` (TIMESTAMP) - Creation timestamp
   - `updated_at` (TIMESTAMP) - Last update timestamp

5. **`order_items`** - Order line items
   - `id` (SERIAL PRIMARY KEY)
   - `order_id` (INTEGER) - Foreign key to orders
   - `product_id` (INTEGER) - Foreign key to products
   - `quantity` (INTEGER) - Item quantity
   - `price` (DECIMAL(10,2)) - Item price at time of order
   - `created_at` (TIMESTAMP) - Creation timestamp

## Setup Instructions

### 1. Environment Variables

Set up the following environment variables:

**For local development:**
```bash
export DB_HOST=localhost
export DB_NAME=ecommerce_db
export DB_USER=ecommerce_user
export DB_PASSWORD=your_strong_password
```

**For production (Netlify):**
```bash
export NETLIFY_DB_URL=your_netlify_database_url
```

### 2. Database Setup

Run the setup script to initialize the database:

```bash
python db/setup.py
```

This will:
- Create all required tables
- Set up indexes for performance
- Insert sample products
- Create triggers for automatic timestamp updates

### 3. Manual Migration

If you prefer to run migrations manually:

```bash
psql -h $DB_HOST -U $DB_USER -d $DB_NAME -f db/migrations/001_initial_schema.sql
```

## Schema Features

### Indexes
- Product name and price indexes for fast searching
- Cart item product ID index for quick lookups
- User email index for authentication
- Order status and user ID indexes for order management

### Foreign Key Constraints
- `cart_items.product_id` → `products.id` (CASCADE DELETE)
- `order_items.order_id` → `orders.id` (CASCADE DELETE)
- `order_items.product_id` → `products.id` (CASCADE DELETE)
- `orders.user_id` → `users.id` (SET NULL on delete)

### Automatic Timestamps
- All tables have `created_at` and `updated_at` columns
- Triggers automatically update `updated_at` on row modifications

## Sample Data

The setup script includes sample products:
- Mythril T-Shirt ($29.99)
- Mythril Hoodie ($49.99)
- Mythril Mug ($12.99)
- Mythril Sticker Pack ($8.99)

## Drizzle ORM Integration

The schema is also defined in TypeScript using Drizzle ORM (`db/schema.ts`) for type-safe database operations in the frontend.

## Troubleshooting

### Common Issues

1. **Connection refused**: Check if PostgreSQL is running and credentials are correct
2. **Permission denied**: Ensure the database user has proper permissions
3. **Table already exists**: The migration uses `CREATE TABLE IF NOT EXISTS` to handle this safely

### Verification

To verify the setup worked correctly:

```sql
-- Check if tables exist
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

-- Check sample products
SELECT * FROM products;

-- Check indexes
SELECT indexname, tablename FROM pg_indexes WHERE schemaname = 'public';
``` 