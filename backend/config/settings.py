# backend/config/settings.py
"""
Application settings and environment variables management.
Loads configurations from .env file with fallback defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load .env file from project root
project_root = Path(__file__).parent.parent.parent
env_path = project_root / '.env'
load_dotenv(env_path)


class Settings:
    """
    Application settings loaded from environment variables.
    All settings have default values for development.
    """
    
    # ============ DATABASE SETTINGS ============
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '5432'))
    DB_NAME: str = os.getenv('DB_NAME', 'ecommerce')
    DB_USER: str = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', 'postgres')
    
    # ============ SECURITY SETTINGS ============
    SECRET_KEY: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_EXPIRATION_HOURS: int = int(os.getenv('JWT_EXPIRATION_HOURS', '8'))
    
    # ============ APPLICATION SETTINGS ============
    APP_NAME: str = os.getenv('APP_NAME', 'E-Commerce Orders')
    APP_VERSION: str = os.getenv('APP_VERSION', '1.0.0')
    DEBUG: bool = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # ============ LOGGING SETTINGS ============
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'logs/app.log')
    
    # ============ PATHS ============
    BASE_DIR: Path = project_root
    LOGS_DIR: Path = project_root / 'logs'
    
    @classmethod
    def validate(cls) -> None:
        """
        Validates critical settings.
        Raises ValueError if production requirements are not met.
        """
        # Check for production secret key
        if cls.SECRET_KEY == 'dev-secret-key-change-in-production':
            if not cls.DEBUG:
                raise ValueError(
                    "SECRET_KEY must be changed in production environment!"
                )
            else:
                print("⚠️  WARNING: Using default SECRET_KEY. Not safe for production!")
        
        # Create logs directory if it doesn't exist
        cls.LOGS_DIR.mkdir(exist_ok=True)
        
        # Validate database settings
        if not cls.DB_HOST:
            raise ValueError("DB_HOST cannot be empty")
        if cls.DB_PORT <= 0 or cls.DB_PORT > 65535:
            raise ValueError(f"Invalid DB_PORT: {cls.DB_PORT}")
        if not cls.DB_NAME:
            raise ValueError("DB_NAME cannot be empty")
    
    @classmethod
    def get_database_url(cls) -> str:
        """
        Returns PostgreSQL connection URL.
        Format: postgresql://user:password@host:port/database
        """
        return (
            f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}"
            f"@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        )
    
    @classmethod
    def get_database_config(cls) -> dict:
        """
        Returns database configuration as a dictionary.
        Useful for psycopg2 connection.
        """
        return {
            'host': cls.DB_HOST,
            'port': cls.DB_PORT,
            'database': cls.DB_NAME,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD
        }
    
    @classmethod
    def display_config(cls) -> None:
        """Prints current configuration (hides sensitive data)."""
        print("\n" + "="*50)
        print(f"📋 {cls.APP_NAME} - Configuration")
        print("="*50)
        print(f"Version:        {cls.APP_VERSION}")
        print(f"Debug Mode:     {cls.DEBUG}")
        print(f"Log Level:      {cls.LOG_LEVEL}")
        print("-"*50)
        print(f"Database:       {cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}")
        print(f"Database User:  {cls.DB_USER}")
        print(f"Secret Key:     {'*' * 10} (hidden)")
        print(f"JWT Expiration: {cls.JWT_EXPIRATION_HOURS}h")
        print("-"*50)
        print(f"Base Directory: {cls.BASE_DIR}")
        print(f"Logs Directory: {cls.LOGS_DIR}")
        print("="*50 + "\n")


# Validate settings on import
Settings.validate()