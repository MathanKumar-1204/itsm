import os
import sys

# Ensure backend root directory is in sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Skip heavy remote model downloads during automated unit tests
os.environ["SKIP_MODEL_DOWNLOAD"] = "true"
os.environ["SERVICENOW_DEMO_MODE"] = "true"
