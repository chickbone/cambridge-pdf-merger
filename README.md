# Cambridge Core PDF Merger

<!-- LATEST_RELEASE_BANNER_START -->
[![Latest Release](https://img.shields.io/github/v/release/chickbone/cambridge-pdf-merger?color=green&label=Latest%20Release)](https://github.com/chickbone/cambridge-pdf-merger/releases/latest)
<!-- LATEST_RELEASE_BANNER_END -->

A specialized Python utility designed to merge individual PDF chapters and sections downloaded from [Cambridge Core](https://www.cambridge.org/core) into a single, well-structured book.

## Features

- **Modern Graphical User Interface (GUI)**: Intuitive CustomTkinter desktop interface with dark/light mode, live progress logs, and file browsing.
- **Automated Merging**: Concatenates multiple PDF files into one.
- **Hierarchical Bookmarks**: Automatically generates a nested table of contents (bookmarks) based on file naming conventions.
- **ZIP Support**: Directly processes ZIP archives downloaded from Cambridge Core.
- **Smart Sorting**: Organizes files numerically based on their chapter/section prefixes (e.g., `01.0`, `01.1`).
- **Flexible CLI**: Supports command-line usage for automated scripting and headless environments.

## Prerequisites

- **Python 3.x**
- **pypdf**
- **customtkinter**

## Installation

### Install from package

Pre-built packages are found on the [Releases](https://github.com/chickbone/cambridge-pdf-merger/releases) page.

### Install from source

```sh
git clone https://github.com/chickbone/cambridge-pdf-merger.git
cd cambridge-pdf-merger
```

### Using [Pipenv](https://pipenv.pypa.io/en/latest/installation.html) (Recommended)

```powershell
# Install dependencies from Pipfile
pipenv install

# Run the app (launches GUI by default)
pipenv run python merge_pdfs.py
```

### Or Using Pip directly

```powershell
pip install pypdf customtkinter
```

## Usage

### 1. Graphical Interface (GUI)
Simply run the script without any arguments:

```powershell
python merge_pdfs.py
# OR
python gui.py
```

In the GUI:
1. Choose whether your source is a **ZIP Archive** or a **PDF Folder**.
2. Click **Browse...** to select your archive or folder (an output name will be auto-suggested).
3. Click **⚡ Merge PDFs** to start merging. Live progress and chapter hierarchy will display in the console.
4. Click **📂 Open Merged File** when complete to view the merged PDF.

### 2. Command Line Interface (CLI)

```powershell
# Merge from a specific ZIP or directory
python merge_pdfs.py my_book.zip
# OR
python merge_pdfs.py ./path/to/pdf_folder

# Specify a custom output name
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

## External links

- https://www.cambridge.org/core
- https://github.com/pcdi/cambridge_core_downloader

## License

This project is open-source. Please refer to the repository's licensing terms (if applicable) for usage permissions.
