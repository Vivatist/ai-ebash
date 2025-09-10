import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # корень проекта
sys.path.insert(0, str(ROOT / "src/ai-bash"))