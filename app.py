import os
import sys
import time
import hashlib
import logging
import logging.handlers
import threading
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from contextlib import contextmanager
from flask import Flask, render_template, request, jsonify
import webview

# Enhanced logging configuration


def setup_logging() -> logging.Logger:
    """Configure logging with rotation and proper error handling."""
    try:
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f"app_{time.strftime('%Y%m%d')}.log"

        # Create formatter

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(threadName)s] - %(message)s"
        )

        # Create handlers

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 5MB
        )
        file_handler.setFormatter(formatter)

        # Get logger

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)

        # Add handlers

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

        return logger
    except Exception as e:
        print(f"Failed to setup logging: {e}")

        # Fallback to basic logging

        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        return logging.getLogger(__name__)


logger = setup_logging()

# File type configurations with more categories


TIPOS_ARQUIVO: Dict[str, List[str]] = {
    "Imagens": [
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
    "Documentos": [
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".rtf",
        ".odt",
        ".xls",
        ".xlsx",
        ".csv",
        ".ppt",
        ".pptx",
    ],
    "Músicas": [
        ".mp3",
        ".wav",
        ".flac",
        ".m4a",
        ".ogg",
        ".wma",
        ".aac",
        ".mid",
        ".midi",
    ],
    "Vídeos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v", ".3gp"],
    "Compactados": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
    "Executáveis": [".exe", ".msi", ".bat", ".cmd", ".com", ".dll"],
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
        ".pl",
    ],
    "3D": [
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
    "Outros": [],
}


# File operation lock


file_locks: Dict[str, threading.Lock] = {}


@contextmanager
def file_lock(filepath: str):
    """Thread-safe file operation context manager."""
    if filepath not in file_locks:
        file_locks[filepath] = threading.Lock()
    try:
        file_locks[filepath].acquire(timeout=5)  # 5 second timeout
        yield
    finally:
        if file_locks[filepath].locked():
            file_locks[filepath].release()


def calculate_file_hash(filepath: Path) -> str:
    """Calculate SHA-256 hash of a file."""
    try:
        hash_sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating file hash for {filepath}: {e}")
        return ""


def is_file_in_use(filepath: Path) -> bool:
    """Check if a file is currently in use."""
    try:
        with open(filepath, "rb") as _:
            return False
    except (IOError, OSError):
        return True


def verificar_permissoes(diretorio: Path) -> Tuple[bool, str]:
    """
    Verify directory permissions with detailed checks.

    Args:
        diretorio: Directory path to check

    Returns:
        Tuple[bool, str]: Success status and message
    """
    try:
        if not diretorio.exists():
            return False, "Directory does not exist"
        # Check read permission

        if not os.access(diretorio, os.R_OK):
            return False, "No read permission"
        # Check write permission

        if not os.access(diretorio, os.W_OK):
            return False, "No write permission"
        # Test file creation

        test_file = diretorio / ".permission_test"
        try:
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            return False, f"Failed to create test file: {e}"
        return True, "All permissions verified"
    except Exception as e:
        logger.error(f"Permission check error: {e}")
        return False, str(e)


def get_safe_filename(filename: str) -> str:
    """Generate a safe filename by removing/replacing unsafe characters."""
    # Remove/replace unsafe characters

    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, "_")
    return filename


class FileOperationResult:
    """Class to store file operation results."""

    def __init__(self, success: bool, message: str, moved_files: int = 0):
        self.success = success
        self.message = message
        self.moved_files = moved_files
        self.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")


def organizar_arquivos(diretorio: str) -> FileOperationResult:
    """
    Organize files with enhanced error handling and safety checks.

    Args:
        diretorio: Directory path to organize

    Returns:
        FileOperationResult: Operation result object
    """
    try:
        logger.info(f"Starting file organization in: {diretorio}")
        diretorio_path = Path(diretorio)

        # Verify directory

        perm_status, perm_message = verificar_permissoes(diretorio_path)
        if not perm_status:
            return FileOperationResult(False, f"Permission error: {perm_message}")
        arquivos_movidos = 0
        erros = []

        # Process each file

        for arquivo in diretorio_path.iterdir():
            if not arquivo.is_file():
                continue
            try:
                # Skip files in use

                if is_file_in_use(arquivo):
                    erros.append(f"File in use: {arquivo.name}")
                    continue
                # Determine file type

                tipo = "Outros"
                for categoria, extensoes in TIPOS_ARQUIVO.items():
                    if arquivo.suffix.lower() in extensoes:
                        tipo = categoria
                        break
                # Create destination folder

                pasta_destino = diretorio_path / tipo
                pasta_destino.mkdir(exist_ok=True)

                # Generate safe filename

                safe_name = get_safe_filename(arquivo.name)
                novo_caminho = pasta_destino / safe_name

                # Handle duplicates

                if novo_caminho.exists():
                    base_name = novo_caminho.stem
                    extension = novo_caminho.suffix
                    counter = 1
                    while novo_caminho.exists():
                        file_hash1 = calculate_file_hash(arquivo)
                        file_hash2 = calculate_file_hash(novo_caminho)

                        # If files are identical, skip

                        if file_hash1 == file_hash2 and file_hash1:
                            logger.info(f"Skipping duplicate file: {arquivo.name}")
                            break
                        novo_caminho = (
                            pasta_destino / f"{base_name}_{counter}{extension}"
                        )
                        counter += 1
                # Move file with lock

                with file_lock(str(arquivo)):
                    if not is_file_in_use(arquivo):
                        arquivo.rename(novo_caminho)
                        arquivos_movidos += 1
                        logger.debug(f"File moved: {arquivo.name} -> {novo_caminho}")
                    else:
                        erros.append(f"File locked during move: {arquivo.name}")
            except Exception as e:
                error_msg = f"Error processing {arquivo.name}: {str(e)}"
                logger.error(error_msg)
                erros.append(error_msg)
        # Generate result message

        message = f"Files organized: {arquivos_movidos}"
        if erros:
            message += f"\nErrors occurred ({len(erros)}):\n" + "\n".join(erros)
        return FileOperationResult(
            success=arquivos_movidos > 0, message=message, moved_files=arquivos_movidos
        )
    except Exception as e:
        logger.exception("Critical error during file organization")
        return FileOperationResult(False, f"Critical error: {str(e)}")


class API:
    """Enhanced API interface with error handling."""

    def escolher_diretorio(self) -> Optional[str]:
        """
        Open directory selection dialog with error handling.

        Returns:
            Optional[str]: Selected directory path or None
        """
        try:
            logger.debug("Opening directory selection dialog")
            diretorio = webview.windows[0].create_file_dialog(webview.FOLDER_DIALOG)

            if not diretorio:
                logger.debug("Directory selection cancelled")
                return None
            selected_dir = diretorio[0]

            # Verify selected directory

            dir_path = Path(selected_dir)
            perm_status, perm_message = verificar_permissoes(dir_path)

            if not perm_status:
                logger.error(f"Permission error for selected directory: {perm_message}")
                return None
            logger.info(f"Directory selected: {selected_dir}")
            return selected_dir
        except Exception as e:
            logger.exception("Error in directory selection")
            return None


# Flask application setup


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max-body-size


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle large request errors."""
    return jsonify({"error": "Request too large"}), 413


@app.route("/")
def index():
    """Route for main page."""
    return render_template("index.html")


@app.route("/organizar", methods=["POST"])
def organizar():
    """Enhanced endpoint for file organization."""
    logger.debug("Received POST request to /organizar")

    try:
        if not request.is_json:
            return jsonify({"error": "Invalid content type"}), 400
        dados = request.get_json()

        if not dados or "diretorio" not in dados:
            return jsonify({"error": "Directory not specified"}), 400
        diretorio = dados["diretorio"]

        if not diretorio or not isinstance(diretorio, str):
            return jsonify({"error": "Invalid directory path"}), 400
        # Organize files

        result = organizar_arquivos(diretorio)

        response = {
            "success": result.success,
            "message": result.message,
            "files_moved": result.moved_files,
            "timestamp": result.timestamp,
        }

        return jsonify(response), 200 if result.success else 500
    except Exception as e:
        logger.exception("Unhandled error processing request")
        return jsonify({"error": f"Server error: {str(e)}"}), 500


def main():
    """Enhanced main application function."""
    logger.info("Starting application")

    try:
        # Check system requirements

        if sys.version_info < (3, 7):
            logger.error("Python 3.7 or higher required")
            sys.exit(1)
        # Initialize API

        api = API()

        # Create window with error handling

        try:
            window = webview.create_window(
                "File Organizer",
                app,
                width=800,
                height=600,
                js_api=api,
                min_size=(400, 300),
            )

            # Set window properties

            window.events.closed += lambda: logger.info("Application window closed")

            logger.info("Window created successfully")
            webview.start()
        except Exception as e:
            logger.error(f"Failed to create window: {e}")
            sys.exit(1)
    except Exception as e:
        logger.exception("Critical error starting application")
        sys.exit(1)


if __name__ == "__main__":
    main()
