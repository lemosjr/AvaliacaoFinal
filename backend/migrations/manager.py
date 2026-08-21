# backend/migrations/manager.py
"""
Migration Manager - Controls database schema versioning.
Automatically discovers and runs migrations in order.
"""

import importlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
import psycopg2

logger = logging.getLogger(__name__)


class MigrationManager:
    """
    Manages database migrations and seeders.
    
    Features:
    - Automatic discovery of migration files
    - Ordered execution by version number
    - Rollback support
    - Seeder execution for initial data
    - Status reporting
    """
    
    def __init__(self, db_config: Dict[str, Any]):
        """
        Initialize the migration manager.
        
        Args:
            db_config: Database connection configuration
        """
        self.db_config = db_config
        self.migrations_dir = Path(__file__).parent / 'versions'
        self.seeders_dir = Path(__file__).parent / 'seeders'
        self._ensure_migrations_table()
    
    def _get_connection(self):
        """Creates a database connection."""
        return psycopg2.connect(**self.db_config)
    
    def _ensure_migrations_table(self) -> None:
        """
        Creates the _migrations control table if it doesn't exist.
        This table tracks which migrations have been executed.
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS _migrations (
                        id SERIAL PRIMARY KEY,
                        version VARCHAR(50) NOT NULL UNIQUE,
                        description TEXT,
                        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        executed_by VARCHAR(100)
                    )
                """)
                conn.commit()
                logger.debug("✅ _migrations table verified/created")
    
    def get_executed_migrations(self) -> List[str]:
        """
        Returns a list of migration versions already executed.
        
        Returns:
            List[str]: List of version numbers (e.g., ['001', '002'])
        """
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT version FROM _migrations ORDER BY id")
                return [row[0] for row in cur.fetchall()]
    
    def get_available_migrations(self) -> List[Dict[str, Any]]:
        """
        Discovers all available migration files in the versions directory.
        
        Returns:
            List[Dict]: Sorted list of migration metadata
        """
        migrations = []
        for file_path in sorted(self.migrations_dir.glob('*.py')):
            if file_path.name == '__init__.py':
                continue
            
            # Extract version from filename (e.g., 001_initial_tables -> 001)
            version = file_path.stem.split('_')[0]
            
            # Validate version format (must be 3 digits)
            if not version.isdigit() or len(version) != 3:
                logger.warning(f"⚠️  Skipping file with invalid version: {file_path.name}")
                continue
            
            migrations.append({
                'file': file_path,
                'module': f"backend.migrations.versions.{file_path.stem}",
                'version': version,
                'full_name': file_path.stem
            })
        
        return sorted(migrations, key=lambda x: x['version'])
    
    def run_migration(self, migration_info: Dict[str, Any]) -> bool:
        """
        Executes a single migration (the 'up' function).
        
        Args:
            migration_info: Migration metadata dictionary
        
        Returns:
            bool: True if successful
        
        Raises:
            Exception: If migration fails
        """
        try:
            # Import the migration module
            module = importlib.import_module(migration_info['module'])
            
            # Check if it has the 'up' function
            if not hasattr(module, 'up'):
                raise ValueError(
                    f"Migration {migration_info['version']} missing 'up()' function"
                )
            
            # Get description
            description = getattr(module, 'DESCRIPTION', migration_info['full_name'])
            
            logger.info(f"📦 Running migration: {migration_info['version']} - {description}")
            
            with self._get_connection() as conn:
                # Execute the migration
                module.up(conn)
                
                # Record the migration
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO _migrations (version, description, executed_by)
                        VALUES (%s, %s, %s)
                    """, (
                        migration_info['version'],
                        description,
                        'system'
                    ))
                conn.commit()
            
            logger.info(f"✅ Migration {migration_info['version']} completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration {migration_info['version']} failed: {str(e)}")
            raise
    
    def rollback_migration(self, version: str) -> bool:
        """
        Rolls back a specific migration (the 'down' function).
        
        Args:
            version: Version number to rollback (e.g., '001')
        
        Returns:
            bool: True if successful
        
        Raises:
            ValueError: If migration file not found or missing 'down' function
        """
        try:
            # Find the migration file
            version_file = None
            for file_path in self.migrations_dir.glob(f'{version}_*.py'):
                if file_path.name != '__init__.py':
                    version_file = file_path
                    break
            
            if not version_file:
                raise ValueError(f"Migration {version} not found")
            
            module_name = f"backend.migrations.versions.{version_file.stem}"
            module = importlib.import_module(module_name)
            
            if not hasattr(module, 'down'):
                raise ValueError(f"Migration {version} missing 'down()' function")
            
            logger.info(f"⬇️  Rolling back migration: {version}")
            
            with self._get_connection() as conn:
                # Execute the rollback
                module.down(conn)
                
                # Remove the migration record
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM _migrations WHERE version = %s", (version,))
                conn.commit()
            
            logger.info(f"✅ Rollback of {version} completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Rollback of {version} failed: {str(e)}")
            raise
    
    def run_all_migrations(self) -> None:
        """
        Runs all pending migrations in order.
        Skips migrations that have already been executed.
        """
        executed = self.get_executed_migrations()
        available = self.get_available_migrations()
        
        pending = [m for m in available if m['version'] not in executed]
        
        if not pending:
            logger.info("✅ No pending migrations")
            return
        
        logger.info(f"📦 Running {len(pending)} pending migration(s)...")
        
        for migration in pending:
            self.run_migration(migration)
        
        logger.info("✅ All migrations completed successfully")
    
    def run_seeders(self) -> None:
        """
        Executes seeders to populate initial data.
        Seeders are only run once (if not already seeded).
        """
        try:
            seeders_file = self.seeders_dir / 'initial_data.py'
            if not seeders_file.exists():
                logger.info("ℹ️  No seeder file found")
                return
            
            # Check if seeders have already been run
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT COUNT(*) FROM _migrations WHERE description = 'seeder'"
                    )
                    count = cur.fetchone()[0]
                    
                    if count > 0:
                        logger.info("ℹ️  Seeders already executed, skipping")
                        return
            
            logger.info("🌱 Running seeders...")
            
            # Import and run the seeder
            module = importlib.import_module("backend.migrations.seeders.initial_data")
            
            if not hasattr(module, 'seed'):
                logger.warning("⚠️  Seeder file missing 'seed()' function")
                return
            
            with self._get_connection() as conn:
                module.seed(conn)
                
                # Record that seeders were executed
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO _migrations (version, description, executed_by)
                        VALUES (%s, %s, %s)
                    """, ('seeder', 'seeder', 'system'))
                conn.commit()
            
            logger.info("✅ Seeders completed successfully")
            
        except Exception as e:
            logger.error(f"❌ Seeder execution failed: {str(e)}")
            raise
    
    def reset_database(self, confirm: bool = False) -> None:
        """
        Resets the entire database (drops all tables and recreates).
        
        WARNING: This deletes ALL data!
        
        Args:
            confirm: Must be True to execute
        """
        if not confirm:
            logger.warning("⚠️  Reset not confirmed. Use confirm=True to force.")
            return
        
        logger.warning("🗑️  RESETTING DATABASE - ALL DATA WILL BE LOST!")
        
        # Get all migrations in reverse order
        available = self.get_available_migrations()
        available.reverse()
        
        # Rollback all migrations
        for migration in available:
            try:
                self.rollback_migration(migration['version'])
            except Exception as e:
                logger.warning(f"Could not rollback {migration['version']}: {str(e)}")
        
        # Drop the migrations table
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS _migrations CASCADE")
                conn.commit()
        
        # Recreate everything
        self._ensure_migrations_table()
        self.run_all_migrations()
        self.run_seeders()
        
        logger.info("✅ Database reset completed")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Returns the current migration status.
        
        Returns:
            dict: Status information
        """
        executed = self.get_executed_migrations()
        available = self.get_available_migrations()
        
        pending = [m for m in available if m['version'] not in executed]
        
        return {
            'total_migrations': len(available),
            'executed_count': len(executed),
            'pending_count': len(pending),
            'executed_versions': executed,
            'pending_versions': [m['version'] for m in pending],
            'all_versions': [m['version'] for m in available]
        }