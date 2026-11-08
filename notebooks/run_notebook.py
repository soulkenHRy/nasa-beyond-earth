"""Turn a '# %%' notebook script into a .ipynb and run every cell, keeping the outputs.

Usage (from the project folder):
    .venv/bin/python notebooks/run_notebook.py notebooks/A_asteroids.py

The .py file is the source; the .ipynb next to it is the executed notebook with all
tables and charts. If a cell fails, the notebook is still saved so the error is visible.
"""
import sys
import time
from pathlib import Path

import jupytext
import nbformat
from nbclient import NotebookClient
from nbclient.exceptions import CellExecutionError

src = Path(sys.argv[1]).resolve()
nb = jupytext.read(src)
nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3 (.venv)", "language": "python"}
out = src.with_suffix(".ipynb")

t0 = time.time()
client = NotebookClient(
    nb, timeout=3600, kernel_name="python3", resources={"metadata": {"path": str(src.parent)}}
)
try:
    client.execute()
except CellExecutionError:
    nbformat.write(nb, out)
    print(f"FAILED after {time.time() - t0:.1f}s; partial notebook saved to {out}")
    raise
nbformat.write(nb, out)
print(f"Ran {src.name} in {time.time() - t0:.1f}s -> {out}")
