# backend/migrations/versions/001_initial_tables.py
"""
Version 001: Create initial tables (products, orders, order_items)
"""

import logging

DESCRIPTION = "Create initial tables: products, orders, order_items"


def up(conn):
    """
    Creates the initial database tables.
    
    Tables created:
    - products: Product catalog with stock
    - orders: Customer orders with status
    - order_items: Line items for each order
    """
    logger = logging.getLogger(__name__)
    logger.info("📝 Creating initial tables...")
    
    with conn.cursor() as cur:
        # ============ PRODUCTS TABLE ============
        cur.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id SERIAL PRIMARY KEY,
                description VARCHAR(200) NOT NULL,
                price DECIMAL(10,2) NOT NULL CHECK (price > 0),
                quantity_available INTEGER NOT NULL CHECK (quantity_available >= 0),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("✅ Table 'products' created")
        
        # ============ ORDERS TABLE ============
        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id SERIAL PRIMARY KEY,
                customer VARCHAR(100) NOT NULL,
                status VARCHAR(20) NOT NULL DEFAULT 'created',
                total_amount DECIMAL(10,2) DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CHECK (status IN ('created', 'processing', 'completed', 'cancelled'))
            )
        """)
        logger.info("✅ Table 'orders' created")
        
        # ============ ORDER ITEMS TABLE ============
        cur.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id SERIAL PRIMARY KEY,
                order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                product_id INTEGER NOT NULL REFERENCES products(id),
                quantity INTEGER NOT NULL CHECK (quantity > 0),
                unit_price DECIMAL(10,2) NOT NULL CHECK (unit_price > 0),
                subtotal DECIMAL(10,2) NOT NULL CHECK (subtotal > 0)
            )
        """)
        logger.info("✅ Table 'order_items' created")
        
        # ============ INDEXES ============
        cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items(product_id)")
        logger.info("✅ Indexes created")
        
        conn.commit()
        logger.info("✅ Initial tables created successfully!")


def down(conn):
    """
    Drops the initial tables (rollback).
    """
    logger = logging.getLogger(__name__)
    logger.warning("🗑️  Dropping initial tables...")
    
    with conn.cursor() as cur:
        # Drop in reverse order due to foreign key constraints
        cur.execute("DROP TABLE IF EXISTS order_items CASCADE")
        cur.execute("DROP TABLE IF EXISTS orders CASCADE")
        cur.execute("DROP TABLE IF EXISTS products CASCADE")
        conn.commit()
    
    logger.info("✅ Initial tables dropped")