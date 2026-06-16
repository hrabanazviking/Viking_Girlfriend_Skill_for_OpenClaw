import os
import sys
import subprocess
import platform
import logging

# Set up logging with a cosmological metaphor
# Huginn and Muninn (Thought and Memory) will guide our logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [ODINS_EYE] - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_command(command: str) -> bool:
    """Check if a command is available on the host system."""
    try:
        import shutil
        if shutil.which(command) is None:
            return False
        subprocess.run([command, "--version"], capture_output=True, check=True) # nosec B603
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def verify_host():
    """Verify the host environment for the Viking Girlfriend skill."""
    logger.info("Starting host verification... [Heimdallr is watching the gates]")
    
    # 1. Check Python Version
    python_version = sys.version_info
    logger.info(f"Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version < (3, 9):
        logger.error("Python 3.9 or higher is required. [The Norns weave a short thread for older versions]")
        return False
    
    # 2. Check OS
    os_name = platform.system()
    logger.info(f"Operating System: {os_name}")
    
    # 3. Check for Podman or Docker
    has_podman = check_command("podman")
    has_docker = check_command("docker")
    
    if has_podman:
        logger.info("Podman detected. [The shield-wall is strong]")
    elif has_docker:
        logger.info("Docker detected. [A reliable galley for your voyage]")
    else:
        logger.warning("Neither Podman nor Docker detected. [The dragon-ship has no oars]")
        logger.warning("Containerization is recommended for the full Ørlög Architecture.")
    
    # 4. Check for GPU (NVIDIA/AMD)
    has_nvidia = check_command("nvidia-smi")
    if has_nvidia:
        logger.info("NVIDIA GPU detected via nvidia-smi. [Thor's hammer sparks are ready]")
    else:
        logger.info("NVIDIA GPU not detected or drivers missing. [Pulling oars manually - CPU mode]")

    # 5. Check dependencies
    logger.info("Verifying Python dependencies... [Mimir's well is deep]")
    try:
        import numpy
        import apscheduler
        import litellm
        import psutil
        logger.info("All core dependencies are already present. [The armory is well-stocked]")
    except ImportError as e:
        logger.warning(f"Missing dependency: {e.name}. [Someone forgot their axe]")
        logger.info("Run 'pip install -r requirements.txt' to install missing dependencies.")
        return False

    logger.info("Host verification complete. [The saga continues...]")
    return True

if __name__ == "__main__":
    try:
        if verify_host():
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred during verification: {e} [The Fenris wolf has broken free!]")
        sys.exit(1)
