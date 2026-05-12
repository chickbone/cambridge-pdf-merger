import os
import re
import zipfile
import shutil
import argparse
from pypdf import PdfWriter, PdfReader

def parse_filename(filename):
    base = os.path.splitext(filename)[0]
    # Match prefix like 04.1
    prefix_match = re.match(r'^(\d+)\.(\d+)', base)
    if not prefix_match:
        return None, None, base.replace('_', ' ')
    
    major = int(prefix_match.group(1))
    minor = int(prefix_match.group(2))
    
    # Extract title
    match = re.search(r'_pp_[^_]+_[^_]+_(.*)$', base)
    if match:
        title = match.group(1).replace('_', ' ')
    else:
        title = re.sub(r'^\d+\.\d+_', '', base).replace('_', ' ')
    
    return major, minor, title

def merge_pdfs_in_dir(directory, output_filename):
    writer = PdfWriter()
    pdf_files = [f for f in os.listdir(directory) if f.endswith('.pdf') and f != output_filename]
    pdf_files.sort()
    
    if not pdf_files:
        print(f"No PDF files found in {directory}")
        return

    print(f"Merging {len(pdf_files)} files from '{directory}' into a tree structure...")
    
    parents = {} # major_index -> parent_outline_item
    current_page = 0

    for filename in pdf_files:
        file_path = os.path.join(directory, filename)
        major, minor, title = parse_filename(filename)
        
        if major is not None and minor == 0:
            parent = writer.add_outline_item(title, page_number=current_page)
            parents[major] = parent
            print(f"Parent: {title}")
        elif major is not None and major in parents:
            writer.add_outline_item(title, page_number=current_page, parent=parents[major])
            print(f"  Child: {title}")
        else:
            writer.add_outline_item(title, page_number=current_page)
            print(f"Top-level: {title}")
            
        writer.append(file_path)
        reader = PdfReader(file_path)
        current_page += len(reader.pages)
    
    with open(output_filename, "wb") as output_stream:
        writer.write(output_stream)
    
    print(f"\nSuccessfully merged into {output_filename}")
def process_zip(zip_path, output_name=None):
    if not os.path.exists(zip_path):
        print(f"Error: ZIP file not found: {zip_path}")
        return

    # Create a temp directory for extraction
    temp_dir = "temp_extracted_pdfs"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    print(f"Extracting {zip_path}...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)

    # Determine output name if not provided
    if not output_name:
        base_name = os.path.splitext(os.path.basename(zip_path))[0]
        # Remove 'cambridge-core_' prefix
        base_name = re.sub(r'^cambridge-core_', '', base_name)
        # Remove trailing date pattern like _12May2026 or _2026May12
        # This regex looks for an underscore followed by common date patterns at the end
        base_name = re.sub(r'_\d{1,2}[a-zA-Z]+\d{4}$', '', base_name)
        base_name = re.sub(r'_\d{4}[a-zA-Z]+\d{1,2}$', '', base_name)

        output_name = base_name + ".pdf"

    merge_pdfs_in_dir(temp_dir, output_name)

    # Cleanup
    shutil.rmtree(temp_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Merge Cambridge Core style PDFs with hierarchical bookmarks.")
    parser.add_argument("input", nargs="?", help="Path to a ZIP file or a directory containing PDFs.")
    parser.add_argument("-o", "--output", help="Name of the output PDF file.")
    
    args = parser.parse_args()

    if args.input:
        if zipfile.is_zipfile(args.input):
            process_zip(args.input, args.output)
        elif os.path.isdir(args.input):
            output = args.output if args.output else "Merged_Document.pdf"
            merge_pdfs_in_dir(args.input, output)
        else:
            print(f"Error: Input '{args.input}' is not a valid ZIP file or directory.")
    else:
        # Default behavior: look for zips, then fall back to current dir
        zips = [f for f in os.listdir('.') if f.endswith('.zip')]
        if zips:
            for z in zips:
                process_zip(z)
        else:
            output = args.output if args.output else "Merged_Document.pdf"
            merge_pdfs_in_dir('.', output)
