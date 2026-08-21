# main.py (raiz do projeto)
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.utils.logger import setup_logging
setup_logging()

from PyQt6.QtWidgets import QApplication
from frontend.src.login_window import LoginWindow
from frontend.src.connectors.auth_connector import AuthConnector
from frontend.src.main_window import MainWindow
from backend.config.database import db
from backend.config.settings import Settings

import logging
logger = logging.getLogger(__name__)


def main():
    """Application entry point."""
    try:
        Settings.validate()
        logger.info(f"🚀 Starting {Settings.APP_NAME} v{Settings.APP_VERSION}")

        # Database initialization
        stats = db.get_stats()
        logger.info(f"📊 Database pool: {stats}")

        # PyQt6 App
        app = QApplication(sys.argv)
        auth_connector = AuthConnector()

        login_window = LoginWindow(auth_connector)
        login_window.login_success.connect(
            lambda user: open_main_window(app, user, auth_connector)
        )
        login_window.show()

        logger.info("✅ Application ready")
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"❌ Application failed: {str(e)}")
        raise


def open_main_window(app, user, auth_connector):
    """Opens the main window."""
    from frontend.src.main_window import MainWindow
    window = MainWindow(user, auth_connector)
    window.show()
    app._main_window = window


if __name__ == "__main__":
    main()