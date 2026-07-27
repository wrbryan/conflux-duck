# Helpers for Colab: create and return Drive-backed workspace and default file paths.
from pathlib import Path
import os

def colab_paths(drive_base='/content/drive/MyDrive', project='conflux-duck-work'):
    """
    Ensure the Drive-based workspace exists and return (workdir, db_path, relationships_path).
    Example return: ('/content/drive/MyDrive/conflux-duck-work',
                     '/content/drive/MyDrive/conflux-duck-work/unified.duckdb',
                     '/content/drive/MyDrive/conflux-duck-work/relationships.json')
    """
    base = Path(drive_base) / project
    base.mkdir(parents=True, exist_ok=True)
    db = base / 'unified.duckdb'
    relationships = base / 'relationships.json'
    return str(base), str(db), str(relationships)

if __name__ == '__main__':
    print(colab_paths())
