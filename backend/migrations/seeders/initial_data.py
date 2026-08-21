# backend/migrations/seeders/initial_data.py
"""
Initial data seeders for development and testing.
Populates the database with sample data.
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def seed(conn):
    """
    Populates the database with initial test data.
    Includes:
    - Default admin user (email: admin@ecommerce.com, password: admin123)
    - Sample products (10 items)
    - Sample orders (5 orders with items)
    """
    logger.info("🌱 Inserting initial data...")
    
    with conn.cursor() as cur:
        # =============================================
        # 1. CREATE DEFAULT ADMIN USER
        # =============================================
        # NOTE: Password is 'admin123' hashed with bcrypt
        # You can change this or regenerate using HashUtils
        admin_password_hash = '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY9YqIhQ7hVpVxK'
        
        cur.execute("""
            INSERT INTO users (email, password_hash, name, is_active)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, ('admin@ecommerce.com', admin_password_hash, 'Administrator', True))
        logger.info("✅ Admin user created (email: admin@ecommerce.com, password: admin123)")
        
        # Get admin user ID
        cur.execute("SELECT id FROM users WHERE email = 'admin@ecommerce.com'")
        admin_id = cur.fetchone()[0]
        
        # =============================================
        # 2. INSERT PRODUCTS
        # =============================================
        products = [
            ('Notebook Dell XPS 13', 7500.00, 10),
            ('Mouse Logitech MX Master 3', 450.00, 25),
            ('Mechanical Keyboard Keychron K2', 600.00, 15),
            ('Monitor LG 27" 4K', 2500.00, 8),
            ('SSD Samsung 1TB NVMe', 800.00, 20),
            ('Gaming Chair DXRacer', 1800.00, 5),
            ('Bluetooth Headphone Sony WH-1000XM4', 1500.00, 12),
            ('Webcam Logitech C920', 400.00, 30),
            ('External HDD 2TB', 500.00, 15),
            ('WiFi 6 Router', 700.00, 10),
        ]
        
        for description, price, quantity in products:
            cur.execute("""
                INSERT INTO products (description, price, quantity_available, user_id)
                VALUES (%s, %s, %s, %s)
            """, (description, price, quantity, admin_id))
        
        logger.info(f"✅ {len(products)} products inserted")
        
        # =============================================
        # 3. INSERT ORDERS
        # =============================================
        orders = [
            ('John Silva', 'completed', 12500.00),
            ('Maria Santos', 'processing', 3800.00),
            ('Peter Oliveira', 'created', 1500.00),
            ('Anna Costa', 'completed', 4500.00),
            ('Carlos Lima', 'cancelled', 0.00),
        ]
        
        for customer, status, total_amount in orders:
            cur.execute("""
                INSERT INTO orders (customer, status, total_amount, user_id)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (customer, status, total_amount, admin_id))
            order_id = cur.fetchone()[0]
            
            # Store order IDs for items
            if customer == 'John Silva':
                order1_id = order_id
            elif customer == 'Maria Santos':
                order2_id = order_id
            elif customer == 'Peter Oliveira':
                order3_id = order_id
            elif customer == 'Anna Costa':
                order4_id = order_id
        
        logger.info(f"✅ {len(orders)} orders inserted")
        
        # =============================================
        # 4. INSERT ORDER ITEMS
        # =============================================
        # Get product IDs
        cur.execute("SELECT id FROM products ORDER BY id")
        product_ids = [row[0] for row in cur.fetchall()]
        
        # Map products for easy reference
        p1, p2, p3, p4, p5, p6, p7, p8, p9, p10 = product_ids[:10]
        
        order_items = [
            # Order 1: John Silva
            (order1_id, p1, 1, 7500.00, 7500.00),
            (order1_id, p2, 2, 450.00, 900.00),
            (order1_id, p3, 1, 600.00, 600.00),
            (order1_id, p4, 1, 2500.00, 2500.00),
            (order1_id, p5, 1, 800.00, 800.00),
            
            # Order 2: Maria Santos
            (order2_id, p5, 3, 800.00, 2400.00),
            (order2_id, p8, 2, 400.00, 800.00),
            (order2_id, p2, 1, 450.00, 450.00),
            
            # Order 3: Peter Oliveira
            (order3_id, p4, 1, 2500.00, 2500.00),
            
            # Order 4: Anna Costa
            (order4_id, p1, 1, 7500.00, 7500.00),
            (order4_id, p2, 2, 450.00, 900.00),
            (order4_id, p7, 1, 1500.00, 1500.00),
        ]
        
        for order_id, product_id, quantity, unit_price, subtotal in order_items:
            cur.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price, subtotal)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, product_id, quantity, unit_price, subtotal))
        
        logger.info(f"✅ {len(order_items)} order items inserted")
        
        # =============================================
        # 5. UPDATE ORDER TOTALS (just in case)
        # =============================================
        cur.execute("""
            UPDATE orders o
            SET total_amount = (
                SELECT COALESCE(SUM(subtotal), 0)
                FROM order_items
                WHERE order_id = o.id
            )
        """)
        logger.info("✅ Order totals updated")
        
        conn.commit()
        logger.info("✅ All seed data inserted successfully!")