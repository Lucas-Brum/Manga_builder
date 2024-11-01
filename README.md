# Manga Builder

![TaoSect Logo](https://taosect.com/wp-content/themes/taosect-theme/img/logo.png)

Manga Builder is a Python script that allows you to extract images from manga chapters on online reading sites and create PDF files to facilitate reading on digital devices like Kindle and Google Play Books (PDFs need to be converted to MOBI for Kindle). 

**Note**: This script currently only works for the site [taosect.com](https://taosect.com/).

## Requirements

This project was developed using Python 3.11.9.

You can install the dependencies using the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Features

- **Chapter Extraction**: The script accesses a manga page and extracts the available chapter links.
- **Image Downloading**: Images from the chapters are downloaded simultaneously, using multiple threads for increased efficiency.
- **PDF Creation**: The images are organized and converted into PDF files, adjusting their size to fit the PDF pages.
- **PDF Grouping**: PDFs are grouped into a specified number of groups (default: 20) and saved in a separate folder.
- **File Cleanup**: Temporary images and folders are removed after the PDFs are created.

## Usage

1. Set the `base_url` variable with the URL of the chapter you want to extract (currently, it can only read mangas from taosect.com).
2. Run the script:

   ```bash
   python manga_builder.py
   ```

3. The PDFs will be generated in the `capitulos_pdf` folder, and the grouped PDFs will be in the `grouped` folder.

---

Enjoy reading your mangas more conveniently!
