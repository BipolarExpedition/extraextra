




## Notes (Not to be included in final version)

`poetry install --extras "7z dev"`

```python
import logging

logger = logging.getLogger(__name__)

try:
    import py7zr
except ImportError:
    py7zr = None
    logger.info("py7zr module is not installed. 7z file handling will not be available.")

# Usage example
def handle_7z_file(file_path):
    if py7zr:
        with py7zr.SevenZipFile(file_path, mode='r') as archive:
            archive.extractall(path='extracted_files')
    else:
        logger.error("7z file handling is not available. Please install py7zr to use this feature.")

# Your main function or other logic
if __name__ == "__main__":
    # Example usage
    handle_7z_file("example.7z")
```

```bash
poetry shell
poetry install
pyinstaller --onefile --hidden-import py7zr  your_script.py
```

```python
# example.spec
a = Analysis(
    ['path/to/your_script.py'],
    pathex=['path/to/your_project'],
    binaries=[],
    datas=[],
    hiddenimports=['tkinter', 'tkinter.filedialog', 'tkinter.messagebox'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)
```

```python
# example.spec

# Import the necessary PyInstaller modules
from PyInstaller.utils.hooks import collect_data_files

# Define the application entry point
a = Analysis(
    ['path/to/your_script.py'],
    pathex=['path/to/your_project'],
    binaries=[],
    datas=collect_data_files('py7zr'),  # Example for including data files
    hiddenimports=['py7zr'],  # List any hidden imports
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
    noarchive=False,
)

# Further configuration for the build process
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='your_application',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
```

