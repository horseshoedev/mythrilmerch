import { integer, pgTable, varchar, text, decimal, timestamp, index } from 'drizzle-orm/pg-core';

// Products table - stores all product information
export const products = pgTable('products', {
    id: integer().primaryKey().generatedAlwaysAsIdentity(),
    name: varchar({ length: 255 }).notNull(),
    description: text().notNull().default(''),
    price: decimal({ precision: 10, scale: 2 }).notNull(),
    imageUrl: varchar({ length: 500 }).notNull().default(''),
    createdAt: timestamp().defaultNow().notNull(),
    updatedAt: timestamp().defaultNow().notNull()
}, (table) => ({
    nameIdx: index('products_name_idx').on(table.name),
    priceIdx: index('products_price_idx').on(table.price)
}));

// Cart items table - stores items in user's shopping cart
export const cartItems = pgTable('cart_items', {
    id: integer().primaryKey().generatedAlwaysAsIdentity(),
    productId: integer().notNull().references(() => products.id, { onDelete: 'cascade' }),
    quantity: integer().notNull().default(1),
    createdAt: timestamp().defaultNow().notNull(),
    updatedAt: timestamp().defaultNow().notNull()
}, (table) => ({
    productIdIdx: index('cart_items_product_id_idx').on(table.productId)
}));

// Users table - for future user authentication
export const users = pgTable('users', {
    id: integer().primaryKey().generatedAlwaysAsIdentity(),
    email: varchar({ length: 255 }).notNull().unique(),
    name: varchar({ length: 255 }).notNull(),
    createdAt: timestamp().defaultNow().notNull(),
    updatedAt: timestamp().defaultNow().notNull()
}, (table) => ({
    emailIdx: index('users_email_idx').on(table.email)
}));

// Orders table - for future order management
export const orders = pgTable('orders', {
    id: integer().primaryKey().generatedAlwaysAsIdentity(),
    userId: integer().references(() => users.id, { onDelete: 'set null' }),
    totalAmount: decimal({ precision: 10, scale: 2 }).notNull(),
    status: varchar({ length: 50 }).notNull().default('pending'),
    createdAt: timestamp().defaultNow().notNull(),
    updatedAt: timestamp().defaultNow().notNull()
}, (table) => ({
    userIdIdx: index('orders_user_id_idx').on(table.userId),
    statusIdx: index('orders_status_idx').on(table.status)
}));

// Order items table - for future order details
export const orderItems = pgTable('order_items', {
    id: integer().primaryKey().generatedAlwaysAsIdentity(),
    orderId: integer().notNull().references(() => orders.id, { onDelete: 'cascade' }),
    productId: integer().notNull().references(() => products.id, { onDelete: 'cascade' }),
    quantity: integer().notNull(),
    price: decimal({ precision: 10, scale: 2 }).notNull(),
    createdAt: timestamp().defaultNow().notNull()
}, (table) => ({
    orderIdIdx: index('order_items_order_id_idx').on(table.orderId),
    productIdIdx: index('order_items_product_id_idx').on(table.productId)
}));

// Keep the posts table for backward compatibility
export const posts = pgTable('posts', {
    id: integer().primaryKey().generatedAlwaysAsIdentity(),
    title: varchar({ length: 255 }).notNull(),
    content: text().notNull().default('')
});