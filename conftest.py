"""Ensure the repository root is importable in tests (so ``import src...`` works)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
