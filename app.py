"""File organization application with GUI using Flask and webview."""

import hashlib
import logging
import logging.handlers
import os
import sys
import threading
import time
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from flask import Flask, jsonify, render_template, request
import webview

# Constants
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB
FILE_CHUNK_SIZE = 65536  # 64KB
LOCK_TIMEOUT = 5  # seconds

FILE_TYPES: Dict[str, List[str]] = {
    "Images": [
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".svg",
        ".webp",
        ".tiff",
        ".ico",
    ],
    "Documents": [
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".rtf",
        ".odt",
        ".xls",
        ".xlsx",
        ".csv",
    ],
    "Audio": [".mp3", ".wav", ".flac", ".m4a", ".ogg", ".wma", ".aac", ".mid", ".midi"],
    "Video": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".3gp"],
    "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "Executables": [".exe", ".msi", ".bat", ".cmd", ".com", ".dll"],
    "Scripts": [
        ".py",
        ".js",
        ".php",
        ".html",
        ".css",
        ".java",
        ".cpp",
        ".c",
        ".cs",
        ".rb",
    ],
    "3D_Models": [
        ".stl",
        ".obj",
        ".fbx",
        ".collada",
        ".3ds",
        ".iges",
        ".step",
        ".x3d",
        ".blend",
    ],
    "Others": [],
}

# Initialize Flask app
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max request size


def configure_logging() -> logging.Logger:
    """Configure logging with rotation and error handling."""
    logger = logging.getLogger(__name__)
    try:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s"
        )

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / f"app_{time.strftime('%Y%m%d')}.log",
            maxBytes=MAX_LOG_SIZE,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)

        logger.setLevel(logging.DEBUG)
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    except Exception as error:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        logger.error("Failed to configure logging: %s", error)

    return logger


logger = configure_logging()
file_locks: Dict[str, threading.Lock] = {}


@contextmanager
def file_lock(filepath: str):
    """Thread-safe file operation context manager."""
    lock = file_locks.setdefault(filepath, threading.Lock())
    try:
        acquired = lock.acquire(timeout=LOCK_TIMEOUT)
        if not acquired:
            raise TimeoutError(
                f"Could not acquire lock for {filepath} within {LOCK_TIMEOUT} seconds"
            )
        yield
    finally:
        if lock.locked():
            lock.release()


class FileOrganizer:
    """Main file organization logic handler."""

    @staticmethod
    def calculate_file_hash(filepath: Path) -> str:
        """Calculate SHA-256 hash of a file's contents."""
        sha256 = hashlib.sha256()
        try:
            with filepath.open("rb") as file:
                while chunk := file.read(FILE_CHUNK_SIZE):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except Exception as error:
            logger.error("Error calculating hash for %s: %s", filepath, error)
            return ""

    @staticmethod
    def check_permissions(directory: Path) -> Tuple[bool, str]:
        """Verify directory permissions and accessibility."""
        try:
            if not directory.exists():
                return False, "Directory does not exist"
            if not os.access(directory, os.R_OK | os.W_OK):
                return False, "Insufficient permissions"

            test_file = directory / ".perm_test"
            try:
                test_file.touch()
                test_file.unlink()
            except OSError as error:
                return False, f"File creation test failed: {error}"

            return True, "Valid permissions"
        except Exception as error:
            logger.error("Permission check failed: %s", error)
            return False, str(error)

    @staticmethod
    def organize_files(directory: str) -> Dict:
        """Organize files in specified directory into categorized subdirectories."""
        result = {
            "success": False,
            "message": "",
            "moved": 0,
            "errors": [],
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }

        try:
            dir_path = Path(directory)
            perm_valid, perm_msg = FileOrganizer.check_permissions(dir_path)
            if not perm_valid:
                result["message"] = f"Permission error: {perm_msg}"
                return result

            for file in dir_path.iterdir():
                if not file.is_file():
                    continue

                try:
                    category = "Others"
                    for file_type, extensions in FILE_TYPES.items():
                        if file.suffix.lower() in extensions:
                            category = file_type
                            break

                    dest_dir = dir_path / category
                    dest_dir.mkdir(exist_ok=True)

                    safe_name = FileOrganizer.sanitize_filename(file.name)
                    dest_path = dest_dir / safe_name

                    if dest_path.exists():
                        if FileOrganizer.is_duplicate(file, dest_path):
                            continue
                        dest_path = FileOrganizer.generate_unique_name(dest_path)

                    with file_lock(str(file)):
                        file.rename(dest_path)
                        result["moved"] += 1

                except Exception as error:
                    error_msg = f"{file.name}: {str(error)}"
                    logger.error(error_msg)
                    result["errors"].append(error_msg)

            result["success"] = result["moved"] > 0
            result["message"] = f"Moved {result['moved']} files"
            if result["errors"]:
                result["message"] += f" with {len(result['errors'])} errors"

        except Exception as error:
            logger.exception("Organization failed")
            result["message"] = f"Critical error: {str(error)}"

        return result

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Remove potentially unsafe characters from filename."""
        unsafe_chars = '<>:"/\\|?*'
        return filename.translate(str.maketrans(unsafe_chars, "_" * len(unsafe_chars)))

    @staticmethod
    def generate_unique_name(path: Path) -> Path:
        """Generate unique filename with incrementing counter."""
        counter = 1
        while path.exists():
            path = path.with_name(f"{path.stem}_{counter}{path.suffix}")
            counter += 1
        return path

    @staticmethod
    def is_duplicate(source: Path, target: Path) -> bool:
        """Check if two files are identical using hash comparison."""
        return FileOrganizer.calculate_file_hash(
            source
        ) == FileOrganizer.calculate_file_hash(target)


class DirectoryAPI:
    """API endpoints for directory operations."""

    def choose_directory(self) -> Optional[str]:
        """Open directory selection dialog."""
        try:
            selected = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)
            if selected:
                return self.validate_directory(Path(selected[0]))
            return None
        except Exception as error:
            logger.error("Directory selection failed: %s", error)
            return None

    def validate_directory(self, path: Path) -> Optional[str]:
        """Validate selected directory permissions."""
        valid, message = FileOrganizer.check_permissions(path)
        if valid:
            return str(path)
        logger.warning("Invalid directory: %s - %s", path, message)
        return None


@app.route("/")
def index():
    """Serve main application interface."""
    return render_template("index.html")


@app.route("/organizar", methods=["POST"])
def organizar_arquivos():
    """Endpoint for file organization."""
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid content type"}), 400

        data = request.get_json()
        if not data.get("diretorio"):
            return jsonify({"error": "Directory not specified"}), 400

        resultado = FileOrganizer.organize_files(data["diretorio"])
        status_code = 200 if resultado["success"] else 500

        return (
            jsonify(
                {
                    "success": resultado["success"],
                    "message": resultado["message"],
                    "moved_files": resultado["moved"],
                    "error_count": len(resultado["errors"]),
                    "timestamp": resultado["timestamp"],
                }
            ),
            status_code,
        )

    except Exception as error:
        logger.error("Unhandled error: %s", str(error))
        return jsonify({"error": "Internal server error", "details": str(error)}), 500


def main():
    """Application entry point."""
    try:
        if sys.version_info < (3, 7):
            logger.error("Requires Python 3.7+")
            sys.exit(1)

        window = webview.create_window(
            "File Organizer",
            app,
            js_api=DirectoryAPI(),  # Certifique-se que está usando a API correta
            width=800,
            height=600,
            min_size=(400, 300),
        )
        window.events.closed += lambda: logger.info("Application closed")
        webview.start()

    except Exception as error:
        logger.critical("Application failed to start: %s", error)
        sys.exit(1)


if __name__ == "__main__":
    main()
