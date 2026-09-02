import os
import re
import sys
import io
import zipfile
import shutil
import argparse
from pypdf import PdfWriter, PdfReader

def parse_filename(filename):
    base = os.path.splitext(filename)[0]
    # Match prefix like 04.1
    prefix_match = re.match(r'^(\d+)\.(\d+)', base)
    if not prefix_match:
        return None, None, base.replace('_', ' '), None
    
    major = int(prefix_match.group(1))
    minor = int(prefix_match.group(2))
    
    # Extract page numbers (e.g. _pp_1_20_ or _p_12_)
    page_str = None
    pp_match = re.search(r'_pp_([^_]+)_([^_]+)_', base)
    if pp_match:
        p_start = pp_match.group(1)
        p_end = pp_match.group(2)
        if p_start == p_end:
            page_str = f"p. {p_start}"
        else:
            page_str = f"p. {p_start}-{p_end}"
    else:
        p_match = re.search(r'_p_([^_]+)_', base)
        if p_match:
            page_str = f"p. {p_match.group(1)}"

    # Extract title
    match = re.search(r'_pp_[^_]+_[^_]+_(.*)$', base)
    if match:
        title = match.group(1).replace('_', ' ')
    else:
        match_single = re.search(r'_p_[^_]+_(.*)$', base)
        if match_single:
            title = match_single.group(1).replace('_', ' ')
        else:
            title = re.sub(r'^\d+\.\d+_', '', base).replace('_', ' ')
    
    return major, minor, title, page_str

def generate_default_output_name(input_path):
    if not input_path:
        return "Merged_Document.pdf"
    base_name = os.path.splitext(os.path.basename(os.path.abspath(input_path)))[0]
    # Remove 'cambridge-core_' prefix
    base_name = re.sub(r'^cambridge-core_', '', base_name)
    # Remove trailing date pattern like _12May2026 or _2026May12
    base_name = re.sub(r'_\d{1,2}[a-zA-Z]+\d{4}$', '', base_name)
    base_name = re.sub(r'_\d{4}[a-zA-Z]+\d{1,2}$', '', base_name)
    if not base_name.strip():
        base_name = "Merged_Document"
    return base_name + ".pdf"

def get_input_structure(input_path):
    """
    Inspects a ZIP file or directory without extraction, returning
    a list of dicts: [{'filename': str, 'major': int|None, 'minor': int|None, 'title': str, 'type': 'parent'|'child'|'top-level', 'page': str|None}]
    """
    if not input_path or not os.path.exists(input_path):
        return []

    pdf_files = []
    if zipfile.is_zipfile(input_path):
        try:
            with zipfile.ZipFile(input_path, 'r') as zf:
                for name in zf.namelist():
                    base_name = os.path.basename(name)
                    if base_name.lower().endswith('.pdf') and not base_name.startswith('.'):
                        pdf_files.append(base_name)
        except Exception:
            return []
    elif os.path.isdir(input_path):
        for name in os.listdir(input_path):
            if name.lower().endswith('.pdf') and not name.startswith('.'):
                pdf_files.append(name)
    
    pdf_files.sort()
    
    parent_majors = set()
    for f in pdf_files:
        major, minor, *_ = parse_filename(f)
        if major is not None and minor == 0:
            parent_majors.add(major)
            
    structure = []
    for f in pdf_files:
        major, minor, title, page_str = parse_filename(f)
        if major is not None and minor == 0:
            item_type = "parent"
        elif major is not None and major in parent_majors:
            item_type = "child"
        else:
            item_type = "top-level"
        structure.append({
            "filename": f,
            "major": major,
            "minor": minor,
            "title": title,
            "type": item_type,
            "page": page_str
        })
    return structure

def get_pdf_metadata_summary(input_path, output_path=None):
    """
    Extracts summary and PDF metadata for either the input source or the generated output PDF.
    """
    summary = {
        "source_name": os.path.basename(input_path) if input_path else "None",
        "file_count": 0,
        "total_pages": 0,
        "title": "Not Specified",
        "author": "Not Specified",
        "subject": "Not Specified",
        "producer": "Not Specified",
        "creation_date": "Not Specified",
        "output_exists": False,
        "output_size_mb": 0.0,
        "output_pages": 0,
    }

    if not input_path or not os.path.exists(input_path):
        return summary

    try:
        if zipfile.is_zipfile(input_path):
            with zipfile.ZipFile(input_path, 'r') as zf:
                pdf_names = [n for n in zf.namelist() if n.lower().endswith('.pdf') and not os.path.basename(n).startswith('.')]
                pdf_names.sort()
                summary["file_count"] = len(pdf_names)
                
                for name in pdf_names:
                    try:
                        pdf_data = zf.read(name)
                        reader = PdfReader(io.BytesIO(pdf_data))
                        summary["total_pages"] += len(reader.pages)
                        if summary["title"] == "Not Specified" and reader.metadata:
                            meta = reader.metadata
                            if meta.title: summary["title"] = str(meta.title)
                            if meta.author: summary["author"] = str(meta.author)
                            if meta.subject: summary["subject"] = str(meta.subject)
                            if meta.producer: summary["producer"] = str(meta.producer)
                            if meta.creation_date: summary["creation_date"] = str(meta.creation_date)
                    except Exception:
                        pass
        elif os.path.isdir(input_path):
            pdf_names = [n for n in os.listdir(input_path) if n.lower().endswith('.pdf') and not n.startswith('.')]
            pdf_names.sort()
            summary["file_count"] = len(pdf_names)
            for name in pdf_names:
                try:
                    fpath = os.path.join(input_path, name)
                    reader = PdfReader(fpath)
                    summary["total_pages"] += len(reader.pages)
                    if summary["title"] == "Not Specified" and reader.metadata:
                        meta = reader.metadata
                        if meta.title: summary["title"] = str(meta.title)
                        if meta.author: summary["author"] = str(meta.author)
                        if meta.subject: summary["subject"] = str(meta.subject)
                        if meta.producer: summary["producer"] = str(meta.producer)
                        if meta.creation_date: summary["creation_date"] = str(meta.creation_date)
                except Exception:
                    pass
    except Exception:
        pass

    if output_path and os.path.exists(output_path):
        try:
            summary["output_exists"] = True
            summary["output_size_mb"] = round(os.path.getsize(output_path) / (1024 * 1024), 2)
            out_reader = PdfReader(output_path)
            summary["output_pages"] = len(out_reader.pages)
            if out_reader.metadata:
                meta = out_reader.metadata
                if meta.title: summary["title"] = str(meta.title)
                if meta.author: summary["author"] = str(meta.author)
                if meta.subject: summary["subject"] = str(meta.subject)
                if meta.producer: summary["producer"] = str(meta.producer)
        except Exception:
            pass

    return summary

def merge_pdfs_in_dir(directory, output_filename, status_callback=print):
    writer = PdfWriter()
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf') and f != os.path.basename(output_filename)]
    pdf_files.sort()
    
    if not pdf_files:
        status_callback(f"No PDF files found in {directory}")
        return False

    status_callback(f"Merging {len(pdf_files)} files from '{directory}' into a tree structure...")
    
    parents = {} # major_index -> parent_outline_item
    current_page = 0

    for filename in pdf_files:
        file_path = os.path.join(directory, filename)
        major, minor, title, *_ = parse_filename(filename)
        
        if major is not None and minor == 0:
            parent = writer.add_outline_item(title, page_number=current_page)
            parents[major] = parent
            status_callback(f"Section: {title}")
        elif major is not None and major in parents:
            writer.add_outline_item(title, page_number=current_page, parent=parents[major])
            status_callback(f"Sub-section: {title}")
        else:
            writer.add_outline_item(title, page_number=current_page)
            status_callback(f"Top-level: {title}")
            
        writer.append(file_path)
        reader = PdfReader(file_path)
        current_page += len(reader.pages)
    
    with open(output_filename, "wb") as output_stream:
        writer.write(output_stream)
    
    status_callback(f"\nSuccessfully merged into {output_filename}")
    return True

def process_zip(zip_path, output_name=None, status_callback=print):
    if not os.path.exists(zip_path):
        status_callback(f"Error: ZIP file not found: {zip_path}")
        return False

    # Create a temp directory for extraction
    temp_dir = "temp_extracted_pdfs"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    status_callback(f"Extracting {zip_path}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Determine output name if not provided
        if not output_name:
            output_name = generate_default_output_name(zip_path)

        success = merge_pdfs_in_dir(temp_dir, output_name, status_callback=status_callback)
        return success
    finally:
        # Cleanup
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

if __name__ == "__main__":
    if len(sys.argv) == 1 or "--gui" in sys.argv:
        try:
            from gui import launch_gui
            launch_gui()
        except ImportError as e:
            print(f"Error launching GUI: {e}")
            print("To run the CLI, supply input arguments: python merge_pdfs.py <input> [-o <output>]")
    else:
        parser = argparse.ArgumentParser(description="Merge Cambridge Core style PDFs with hierarchical bookmarks.")
        parser.add_argument("input", help="Path to a ZIP file or a directory containing PDFs.")
        parser.add_argument("-o", "--output", help="Name of the output PDF file.")
        
        args = parser.parse_args()

        if zipfile.is_zipfile(args.input):
            process_zip(args.input, args.output)
        elif os.path.isdir(args.input):
            output = args.output if args.output else generate_default_output_name(args.input)
            merge_pdfs_in_dir(args.input, output)
        else:
            print(f"Error: Input '{args.input}' is not a valid ZIP file or directory.")
