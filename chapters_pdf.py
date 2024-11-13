import os
from PIL import Image
from fpdf import FPDF
import tempfile
from natsort import natsorted  # Natural sorting for proper ordering of files

# Directory paths for input images and output PDFs
output_directory = './chapters'

def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)

def collect_images_from_folder(folder_path):
    images = []
    for file_name in os.listdir(folder_path):
        if is_image_file(file_name):
            image_path = os.path.join(folder_path, file_name)
            images.append((file_name, Image.open(image_path)))
    return natsorted(images, key=lambda x: x[0])

def is_image_file(file_name):
    return file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))

def create_pdf_from_images(images, pdf_name):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    for _, img in images:
        add_image_to_pdf(pdf, img)
    
    save_pdf(pdf, pdf_name)

def add_image_to_pdf(pdf, image):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        temp_image_path = temp_file.name
        image.save(temp_image_path, 'PNG')
        
    pdf.add_page()
    pdf.image(temp_image_path, x=10, y=10, w=180)
    os.remove(temp_image_path)

def save_pdf(pdf, pdf_name):
    pdf_output_path = os.path.join(output_directory, f"{pdf_name}.pdf")
    pdf.output(pdf_output_path)
    print(f'Generated PDF: "{pdf_output_path}"')

def process_folders_in_directory(base_dir):
    ensure_directory_exists(output_directory)
    for root, _, _ in os.walk(base_dir):
        folder_name = os.path.basename(root)
        images = collect_images_from_folder(root)
        if images:
            create_pdf_from_images(images, folder_name)
