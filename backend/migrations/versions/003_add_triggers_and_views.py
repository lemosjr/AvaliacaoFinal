# backend/migrations/versions/003_add_triggers_and_views.py
"""
Version 003: Add triggers for auto-update timestamps and views for reporting
"""

import logging

DESCRIPTION = "Add triggers for updated_at and reporting views"


def up(conn):
    """
    Adds triggers and views for better data management.
    """
    logger = logging.getLogger(__name__)
    logger.info("📝 Adding triggers and views...")
    
    with conn.cursor() as cur:
        # ============ TRIGGER FUNCTION ============
        cur.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE 'plpgsql'
        """)
        logger.info("✅ Function update_updated_at_column created")
        
        # ============ TRIGGER FOR PRODUCTS ============
        cur.execute("""
            DROP TRIGGER IF EXISTS trigger_update_product_updated_at ON products;
            CREATE TRIGGER trigger_update_product_updated_at
                BEFORE UPDATE ON products
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column()
        """)
        logger.info("✅ Trigger on products created")
        
        # ============ TRIGGER FOR ORDERS ============
        cur.execute("""
            DROP TRIGGER IF EXISTS trigger_update_order_updated_at ON orders;
            CREATE TRIGGER trigger_update_order_updated_at
                BEFORE UPDATE ON orders
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column()
        """)
        logger.info("✅ Trigger on orders created")
        
        # ============ VIEW: ORDER REPORT ============
        cur.execute("""
            CREATE OR REPLACE VIEW vw_order_report AS
            SELECT 
                o.id AS order_id,
                o.customer,
                o.status,
                o.total_amount,
                o.created_at,
                u.name AS user_name,
                u.email AS user_email,
                COUNT(oi.id) AS total_items,
                COALESCE(SUM(oi.quantity), 0) AS total_quantity
            FROM orders o
            LEFT JOIN users u ON u.id = o.user_id
            LEFT JOIN order_items oi ON oi.order_id = o.id
            GROUP BY o.id, u.id
            ORDER BY o.created_at DESC
        """)
        logger.info("✅ View vw_order_report created")
        
        # ============ VIEW: PRODUCT INVENTORY ============
        cur.execute("""
            CREATE OR REPLACE VIEW vw_product_inventory AS
            SELECT 
                p.id AS product_id,
                p.description,
                p.price,
                p.quantity_available,
                p.created_at,
                u.name AS user_name,
                COALESCE(SUM(oi.quantity), 0) AS total_ordered
            FROM products p
            LEFT JOIN users u ON u.id = p.user_id
            LEFT JOIN order_items oi ON oi.product_id = p.id
            GROUP BY p.id, u.id
            ORDER BY p.id
        """)
        logger.info("✅ View vw_product_inventory created")
        
        conn.commit()
        logger.info("✅ Triggers and views added successfully!")


def down(conn):
    """
    Removes triggers and views (rollback).
    """
    logger = logging.getLogger(__name__)
    logger.warning("🗑️  Removing triggers and views...")
    
    with conn.cursor() as cur:
        cur.execute("DROP VIEW IF EXISTS vw_order_report CASCADE")
        cur.execute("DROP VIEW IF EXISTS vw_product_inventory CASCADE")
        cur.execute("DROP TRIGGER IF EXISTS trigger_update_product_updated_at ON products")
        cur.execute("DROP TRIGGER IF EXISTS trigger_update_order_updated_at ON orders")
        cur.execute("DROP FUNCTION IF EXISTS update_updated_at_column CASCADE")
        conn.commit()
    
    logger.info("✅ Triggers and views removed")