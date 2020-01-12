import os
import sys

if hasattr(sys, 'frozen'):
    PYTHON_FOLDER = os.path.dirname(sys.executable)
else:
    PYTHON_FOLDER = os.path.dirname(os.path.abspath('__file__'))
CONFIG_FOLDER = os.path.join(PYTHON_FOLDER, 'config')
LOG_FOLDER = os.path.join(PYTHON_FOLDER, "logs")
HTTP_FOLDER = os.path.join(PYTHON_FOLDER, 'http')
