import os
from natsort import natsorted
from PyPDF2 import PdfWriter, PdfReader

# Directory paths for input PDFs and output merged PDFs
pdf_folder = './chapters'
merged_folder = './merged_chapters'

def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def get_pdf_files(directory_path):
    return natsorted([f for f in os.listdir(directory_path) if f.endswith('.pdf')])

def split_into_groups(files, group_size=20):
    return [files[i:i + group_size] for i in range(0, len(files), group_size)]

def merge_pdfs(pdf_files, output_path):
    writer = PdfWriter()
    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        add_pdf_to_writer(writer, pdf_path)
    save_writer_to_file(writer, output_path)

def add_pdf_to_writer(writer, pdf_path):
    try:
        with open(pdf_path, 'rb') as pdf_file:
            reader = PdfReader(pdf_file)
            writer.append_pages_from_reader(reader)
    except Exception as e:
        print(f"Error adding {pdf_path}: {e}")

def save_writer_to_file(writer, output_path):
    with open(output_path, 'wb') as output_file:
        writer.write(output_file)
    print(f'Merged PDF saved as "{output_path}"')

def get_grouped_pdf_name(first_pdf, last_pdf):
    first_name = first_pdf.replace('.pdf', '')
    last_name = last_pdf.replace('.pdf', '')
    return f"{first_name}_to_{last_name}.pdf"

def merge_pdf_groups():
    ensure_directory_exists(merged_folder)
    pdf_files = get_pdf_files(pdf_folder)
    pdf_groups = split_into_groups(pdf_files)

    for group in pdf_groups:
        output_file_name = get_grouped_pdf_name(group[0], group[-1])
        output_path = os.path.join(merged_folder, output_file_name)
        merge_pdfs(group, output_path)