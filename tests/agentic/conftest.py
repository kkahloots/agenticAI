"""conftest.py for tests/agentic/ — ensures project root is on sys.path."""
import sys
from pathlib import Path

# Add project root so all agentic.* imports resolve correctly
_root = Path(__file__).parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))
