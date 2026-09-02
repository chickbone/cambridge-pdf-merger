# Cambridge Core PDF Merger

A specialized Python utility for merging individual PDF chapters and sections into a single, structured book. This tool is specifically designed to handle the ZIP archives and naming conventions used by Cambridge Core.

## Overview

The merger automates the assembly of fragmented PDF files into a cohesive document, complete with a hierarchical table of contents (bookmarks) derived from the file metadata and naming structure. It features both a modern CustomTkinter Graphical User Interface (GUI) and a Command-Line Interface (CLI).

### Key Components

- **`merge_pdfs.py`**: The primary backend execution script that handles ZIP extraction, logical sorting, and PDF concatenation, and acts as the entry point.
- **`gui.py`**: The CustomTkinter graphical desktop interface.
- **Naming Convention (`XX.Y_pp_...pdf`)**: Files are sorted numerically by their prefix. 
  - `XX.0` indicates a primary chapter heading.
  - `XX.Y` indicates a nested sub-section.

## Usage: Merging the PDFs

The project includes both a GUI and a CLI to rebuild full books from constituent PDF parts or ZIP archives.

### Prerequisites
- Python 3.x
- `pypdf` library
- `customtkinter` library

You can set up the environment using **pipenv**:
```powershell
# Install dependencies from Pipfile
pipenv install

# Run the app (launches GUI by default)
pipenv run python merge_pdfs.py
```
Alternatively, install directly via pip:
`pip install pypdf customtkinter`

### Execution

1.  **GUI Mode (Default):**
    ```powershell
    python merge_pdfs.py
    # OR
    python gui.py
    ```
    - Launches the interactive CustomTkinter desktop interface with file browsing, theme toggle, and live progress logging.

2.  **CLI - Specific ZIP/Directory:**
    ```powershell
    python merge_pdfs.py my_book.zip
    # OR
    python merge_pdfs.py ./path/to/pdf_folder
    ```

3.  **CLI - Custom Output Name:**
    ```powershell
    python merge_pdfs.py my_book.zip -o Final_Book.pdf
    ```

### Building the Executable (Local)
If you want to build the `.exe` locally on Windows:
```powershell
pipenv install --dev
pipenv run pyinstaller --onefile --noconsole --name cambridge-pdf-merger merge_pdfs.py
```
The executable will be generated in the `dist/` folder.

### Automated Releases (GitHub Actions)
A GitHub Actions workflow is configured to automatically build and release the executable:
1.  **Tag the release**: Push a tag starting with `v` (e.g., `v1.0.0`).
    ```powershell
    git tag v1.0.0
    git push origin v1.0.0
    ```
2.  **Wait for Build**: The "Build and Release" workflow will trigger on the Windows runner.
3.  **Download Asset**: Once finished, the `cambridge-pdf-merger.exe` will be attached to the new GitHub Release.

### Script Logic
The `merge_pdfs.py` script performs the following:
1.  **CLI/GUI Routing:** Checks command line arguments; launches the CustomTkinter GUI if no input arguments are given, or runs CLI mode if input is provided.
2.  **ZIP Handling:** Uses `zipfile` and `shutil` for extraction and cleanup.
3.  **Ordering:** Sorts PDF files alphabetically based on their numerical prefix (`XX.Y`).
4.  **Parsing:** Extracts descriptive titles from the filenames.
5.  **Hierarchy:** Identifies `XX.0` files as parent chapters and nests `XX.Y` files beneath them.
6.  **Concatenation:** Merges all files with a hierarchical bookmark tree, reporting status via callbacks.
