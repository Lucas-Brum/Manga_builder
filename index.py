from image_downloader import download_manga_chapters
from chapters_pdf import process_folders_in_directory
from union_pdf import merge_pdf_groups
from delete_old_files import remover_pasta

link = input("Digite o link do mangá que você deseja baixar: ")

download_manga_chapters(link)
process_folders_in_directory('./manga_images')
remover_pasta('manga_images')
merge_pdf_groups()
remover_pasta('chapters')
