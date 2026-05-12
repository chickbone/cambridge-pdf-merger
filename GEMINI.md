# Cambridge Core PDF Merger

A specialized Python utility for merging individual PDF chapters and sections into a single, structured book. This tool is specifically designed to handle the ZIP archives and naming conventions used by Cambridge Core.

## Overview

The merger automates the assembly of fragmented PDF files into a cohesive document, complete with a hierarchical table of contents (bookmarks) derived from the file metadata and naming structure.

### Key Components

- **`merge_pdfs.py`**: The primary execution script that handles ZIP extraction, logical sorting, and PDF concatenation.
- **Naming Convention (`XX.Y_pp_...pdf`)**: Files are sorted numerically by their prefix. 
  - `XX.0` indicates a primary chapter heading.
  - `XX.Y` indicates a nested sub-section.

## Usage: Merging the PDFs

The project includes a specialized script to rebuild full books from constituent PDF parts or ZIP archives.

### Prerequisites
- Python 3.x
- `pypdf` library

You can set up the environment using **pipenv**:
```powershell
# Install dependencies from Pipfile
pipenv install

# Run the script within the virtualenv
pipenv run python merge_pdfs.py
```
Alternatively, install directly via pip:
`pip install pypdf`

### Execution
The script now supports command-line arguments for greater flexibility:

1.  **Automatic Mode (Default):**
    ```powershell
    python merge_pdfs.py
    ```
    - Processes all `.zip` files in the current folder.
    - If no ZIPs are found, merges PDFs in the current folder into `Merged_Document.pdf`.

2.  **Specific ZIP/Directory:**
    ```powershell
    python merge_pdfs.py my_book.zip
    # OR
    python merge_pdfs.py ./path/to/pdf_folder
    ```

3.  **Custom Output Name:**
    ```powershell
    python merge_pdfs.py my_book.zip -o Final_Book.pdf
    ```

### Script Logic
The `merge_pdfs.py` script performs the following:
1.  **CLI Arguments:** Uses `argparse` to handle user-specified inputs and outputs.
2.  **ZIP Handling:** Uses `zipfile` and `shutil` for extraction and cleanup.
3.  **Ordering:** Sorts PDF files alphabetically based on their numerical prefix (`XX.Y`).
3.  **Parsing:** Extracts descriptive titles from the filenames.
4.  **Hierarchy:** Identifies `XX.0` files as parent chapters and nests `XX.Y` files beneath them.
5.  **Concatenation:** Merges all files with a hierarchical bookmark tree.
