# backend/migrations/versions/002_add_user_table.py
"""
Version 002: Add user table and relationships
"""

import logging

DESCRIPTION = "Add user table with authentication support"


def up(conn):
    """
    Adds the users table and links products/orders to users.
    """
    logger = logging.getLogger(__name__)
    logger.info("📝 Adding user table...")
    
    with conn.cursor() as cur:
        # ============ USERS TABLE ============
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                name VARCHAR(100) NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP
            )
        """)
        logger.info("✅ Table 'users' created")
        
        # ============ ADD FOREIGN KEY TO PRODUCTS ============
        cur.execute("""
            ALTER TABLE products 
            ADD COLUMN IF NOT EXISTS user_id INTEGER 
            REFERENCES users(id) ON DELETE CASCADE
        """)
        logger.info("✅ Added user_id to products")
        
        # ============ ADD FOREIGN KEY TO ORDERS ============
        cur.execute("""
            ALTER TABLE orders 
            ADD COLUMN IF NOT EXISTS user_id INTEGER 
            REFERENCES users(id) ON DELETE CASCADE
        """)
        logger.info("✅ Added user_id to orders")
        
        # ============ INDEXES ============
        cur.execute("CREATE INDEX IF NOT EXISTS idx_products_user ON products(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_user ON orders(user_id)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        logger.info("✅ Indexes created")
        
        conn.commit()
        logger.info("✅ User table added successfully!")


def down(conn):
    """
    Removes the user table and related columns.
    """
    logger = logging.getLogger(__name__)
    logger.warning("🗑️  Removing user table...")
    
    with conn.cursor() as cur:
        cur.execute("ALTER TABLE products DROP COLUMN IF EXISTS user_id")
        cur.execute("ALTER TABLE orders DROP COLUMN IF EXISTS user_id")
        cur.execute("DROP TABLE IF EXISTS users CASCADE")
        conn.commit()
    
    logger.info("✅ User table removed")