from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def initialize_driver():
    return webdriver.Chrome()

def open_url(driver, url):
    driver.get(url)

def setup_wait(driver, seconds=10):
    return WebDriverWait(driver, seconds)

def find_select_element(driver, by, identifier):
    return driver.find_element(by, identifier)

def find_options(select_element, tag_name):
    return select_element.find_elements(By.TAG_NAME, tag_name)

def get_chapter_url(option):
    return option.get_attribute("data-url")

def refresh_elements(wait, by, identifier, tag_name):
    select_element = wait.until(EC.presence_of_element_located((by, identifier)))
    return find_options(select_element, tag_name)

def get_chapter_name(wait, xpath):
    name = wait.until(EC.presence_of_element_located((By.XPATH, xpath))).text
    return name.replace('.', 'v')

def create_directory(directory_path):
    os.makedirs(directory_path, exist_ok=True)

def find_images(driver, xpath):
    return driver.find_elements(By.XPATH, xpath)

def download_image_with_retry(url, retries=3, delay=2):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.content
        except requests.exceptions.RequestException:
            time.sleep(delay)
    return None

def save_image(directory, chapter_name, index, content):
    filename = f"{directory}/{chapter_name} - {index}.jpg"
    with open(filename, "wb") as f:
        f.write(content)

def download_image(image_url, directory, chapter_name, index):
    content = download_image_with_retry(image_url)
    if content:
        save_image(directory, chapter_name, index, content)
        print(f"Downloaded image {index} for chapter {chapter_name}")
    else:
        print(f"Failed to download image {index} for chapter {chapter_name}")

def download_images_in_parallel(driver, chapter_name, max_workers=5):
    directory_path = f"manga_images/{chapter_name}"
    create_directory(directory_path)
    images = find_images(driver, "//img[contains(@src, 'drive.google.com')]")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(download_image, img.get_attribute("src"), directory_path, chapter_name, i)
            for i, img in enumerate(images, start=1)
        ]
        for future in as_completed(futures):
            future.result()

def download_chapter(driver, wait, options, index):
    options = refresh_elements(wait, By.ID, "leitor_capitulo_projeto", "option")
    chapter_url = get_chapter_url(options[index])
    open_url(driver, chapter_url)
    chapter_name = get_chapter_name(wait, "//a[contains(@href, '/projeto/one-punch-man/')]")
    download_images_in_parallel(driver, chapter_name)

def close_driver(driver):
    driver.quit()

def download_manga_chapters(link):
    driver = initialize_driver()
    open_url(driver, link)
    wait = setup_wait(driver)
    select_element = find_select_element(driver, By.ID, "leitor_capitulo_projeto")
    options = find_options(select_element, "option")
    
    for index in range(len(options)):
        download_chapter(driver, wait, options, index)
    
    close_driver(driver)
