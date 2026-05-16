from pathlib import Path
import runpy

root_dashboard = Path(__file__).resolve().parents[1] / "dashboard.py"

runpy.run_path(str(root_dashboard))
