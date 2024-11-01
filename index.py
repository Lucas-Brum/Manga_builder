import os
from natsort import natsorted
from PyPDF2 import PdfWriter, PdfReader
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
import requests
from PIL import Image
from io import BytesIO
from reportlab.pdfgen import canvas
import time
import shutil  # Import shutil for removing directories

def configure_driver():
    return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

def access_main_page(driver, url):
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    return wait.until(EC.presence_of_element_located((By.ID, "leitor_capitulo_projeto")))

def extract_chapter_links(select_element):
    options = select_element.find_elements(By.TAG_NAME, "option")
    return [(option.get_attribute("data-url"), option.get_attribute("value")) for option in options]

def download_image(img_url, img_name):
    try:
        response = requests.get(img_url, timeout=10)
        response.raise_for_status()
        image = Image.open(BytesIO(response.content))
        image.save(img_name)
        return img_name
    except Exception:
        return None

def download_chapter_images(driver, images_folder):
    img_tags = driver.find_elements(By.CLASS_NAME, 'pagina_capitulo')
    with ThreadPoolExecutor() as executor:
        return list(filter(None, executor.map(
            lambda img: download_image(
                img.get_attribute('src'),
                os.path.join(images_folder, f"{img.get_attribute('alt') or 'image_without_alt'}.png").replace('/', '_')
            ),
            img_tags
        )))

def create_pdf(pdf_path, image_paths):
    c = canvas.Canvas(pdf_path)
    page_width, page_height = c._pagesize

    for img_path in image_paths:
        img = Image.open(img_path)
        new_width, new_height = adjust_image_size(img, page_width, page_height)
        c.drawImage(img_path, 0, page_height - new_height, width=new_width, height=new_height)
        c.showPage()

    c.save()

def adjust_image_size(img, page_width, page_height):
    aspect = img.height / float(img.width)
    if img.width > page_width or img.height > page_height:
        new_width = page_width
        new_height = page_width * aspect
        if new_height > page_height:
            new_height = page_height
            new_width = page_height / aspect
    else:
        new_width, new_height = img.width, img.height
    return new_width, new_height

def remove_image_with_retries(image_path, attempts=3, interval=0.5):
    for attempt in range(attempts):
        try:
            os.unlink(image_path)
            return True
        except PermissionError:
            time.sleep(interval)
    return False

def remove_images(image_paths):
    for img_path in image_paths:
        remove_image_with_retries(img_path)

def remove_image_folder(images_folder):
    try:
        os.rmdir(images_folder)
    except Exception:
        pass

def extract_chapter_title(driver):
    try:
        title_element = driver.find_element(By.XPATH, '//a[contains(@href, "one-punch-man")]')
        return title_element.text.strip()
    except Exception:
        return "Unknown_Chapter"

def format_pdf_name(title):
    if "Capítulo" in title:
        part_number = title.split("Capítulo ")[-1]
        if "." in part_number:
            title = title.replace(f"Capítulo {part_number}", f"Capítulo 0{part_number}")
    
    pdf_name = title.replace(" - ", "_").replace(" ", "_").replace(".", "v")
    return f"{pdf_name}.pdf"

def download_and_create_pdfs(base_url):
    driver = configure_driver()
    select_element = access_main_page(driver, base_url)
    chapter_links = extract_chapter_links(select_element)
    os.makedirs('capitulos_pdf', exist_ok=True)
    
    images_folder = 'images'
    os.makedirs(images_folder, exist_ok=True)

    for link, chapter_id in chapter_links:
        driver.get(link)
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'pagina_capitulo')))
        
        image_paths = download_chapter_images(driver, images_folder)
        if image_paths:
            chapter_title = extract_chapter_title(driver)
            pdf_name = format_pdf_name(chapter_title)
            pdf_path = os.path.join('capitulos_pdf', pdf_name)
            create_pdf(pdf_path, image_paths)
            remove_images(image_paths)

    driver.quit()
    remove_image_folder(images_folder)

def group_pdf_names(pdf_folder, group_size=20):
    try:
        pdf_names = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]
        pdf_names = natsorted(pdf_names)
        pdf_groups = [pdf_names[i:i + group_size] for i in range(0, len(pdf_names), group_size)]
        return pdf_groups
    except FileNotFoundError:
        return []

def create_grouped_pdf(pdf_folder, group, grouped_folder='./grouped'):
    writer = PdfWriter()
    for pdf in group:
        pdf_path = os.path.join(pdf_folder, pdf)
        try:
            with open(pdf_path, 'rb') as f:
                writer.append_pages_from_reader(PdfReader(f))
        except Exception:
            continue

    os.makedirs(grouped_folder, exist_ok=True)
    grouped_pdf_name = f"{group[0].replace('.pdf', '')}_to_{group[-1].replace('.pdf', '')}.pdf"
    grouped_pdf_path = os.path.join(grouped_folder, grouped_pdf_name)

    with open(grouped_pdf_path, 'wb') as f_out:
        writer.write(f_out)

def remove_folder(folder):
    """Remove the specified folder and all its contents."""
    try:
        shutil.rmtree(folder)
        print(f"The folder '{folder}' and all its contents have been removed.")
    except Exception as e:
        print(f"Error removing folder '{folder}': {e}")

base_url = "https://taosect.com/leitor-online/projeto/one-punch-man/cap-tulo-01/"
download_and_create_pdfs(base_url)

pdf_folder = "./capitulos_pdf"
groups = group_pdf_names(pdf_folder)

for group in groups:
    create_grouped_pdf(pdf_folder, group)

remove_folder(pdf_folder)
