# -----------------
# | CONFIGURATION |
# -----------------
from configparser import ConfigParser
import os
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')

config = ConfigParser()
read_files = config.read(config_path)
if not read_files:
    raise FileNotFoundError(f"Could not read config file at {config_path}")


# -------------
# | CONSTANTS |
# -------------
MAX_WORKERS = config.getint('GRPC', 'max_workers')
PORT = config.getint('GRPC', 'port')