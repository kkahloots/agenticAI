"""Centralized path setup for notebook utilities."""
import sys
from pathlib import Path

# Get project root: notebooks/nonagent/utils -> agenticAI
_PROJECT_ROOT = Path(__file__).parent.parent.parent

# Add to sys.path immediately and ensure it stays
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

def ensure_project_path():
    """Ensure project root is in sys.path for src imports."""
    if str(_PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(_PROJECT_ROOT))
    return _PROJECT_ROOT
