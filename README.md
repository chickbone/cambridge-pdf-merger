# Cambridge Core PDF Merger

A specialized Python utility designed to merge individual PDF chapters and sections—typically downloaded from Cambridge Core—into a single, professionally structured book.

## Features

- **Automated Merging**: Concatenates multiple PDF files into one.
- **Hierarchical Bookmarks**: Automatically generates a nested table of contents (bookmarks) based on file naming conventions.
- **ZIP Support**: Directly processes ZIP archives downloaded from Cambridge Core.
- **Smart Sorting**: Organizes files numerically based on their chapter/section prefixes (e.g., `01.0`, `01.1`).
- **Flexible CLI**: Supports custom input files/directories and output names.

## Prerequisites

- **Python 3.x**
- **pypdf** library

## Installation

### Using [Pipenv](https://pipenv.pypa.io/en/latest/installation.html) (Recommended)

```powershell
# Install dependencies from Pipfile
pipenv install

# Run the script within the virtualenv
pipenv run python merge_pdfs.py
```

### Using Pip

```powershell
pip install pypdf
```

## Usage

The script is designed to be run from the command line with several modes:

### 1. Automatic Mode (Default)
Processes all `.zip` files in the current folder. If no ZIPs are found, it merges all PDFs in the current folder into `Merged_Document.pdf`.

```powershell
python merge_pdfs.py
```

### 2. Specific ZIP or Directory
Specify a particular ZIP archive or a folder containing PDF files.

```powershell
python merge_pdfs.py my_book.zip
# OR
python merge_pdfs.py ./path/to/pdf_folder
```

### 3. Custom Output Name
Use the `-o` or `--output` flag to define the resulting file name.

```powershell
python merge_pdfs.py my_book.zip -o "Final_Book_Name.pdf"
```

## Naming Convention

To ensure correct sorting and bookmark nesting, the script expects the following naming format:

- **`XX.0_...pdf`**: Interpreted as a primary **Chapter** heading.
- **`XX.Y_...pdf`**: Interpreted as a **Sub-section** nested under the corresponding `XX.0` chapter.

The numerical prefix (`XX.Y`) is used for logical ordering, while the remaining part of the filename is parsed to create the bookmark title.

## How it Works

1. **Extraction**: If a ZIP is provided, it extracts the contents to a temporary directory.
2. **Analysis**: It scans the target folder for PDF files and parses their numerical prefixes.
3. **Sorting**: Files are sorted numerically to maintain the book's intended structure.
4. **Assembly**: It uses `pypdf` to concatenate the files, injecting hierarchical bookmarks as it goes.
5. **Cleanup**: Temporary extraction folders are removed after processing.

## License

This project is open-source. Please refer to the repository's licensing terms (if applicable) for usage permissions.
