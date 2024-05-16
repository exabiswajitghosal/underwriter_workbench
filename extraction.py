import zipfile
import os
import shutil
from pdf2image import convert_from_path


def extract_files(source_location=None, destination_location=None):
    destination_location += "/user_id"
    # Create the directory if it doesn't exist
    if not os.path.exists(destination_location):
        os.makedirs(destination_location)

    # Open the ZIP file
    with zipfile.ZipFile(source_location, 'r') as zip_ref:
        zip_ref.extractall(destination_location)

    res = "Files extracted successfully to " + destination_location
    return res


def pdf_to_jpg(file_path, output_dir):
    # Create output directory
    output_dir += "/"+(file_path.split('/')[-1]).split('.')[0]
    if os.path.exists(output_dir):
        # Remove output directory and its contents
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    # Convert PDF to images
    images = convert_from_path(file_path)

    # Save images as JPG files
    for i, image in enumerate(images):
        image_path = os.path.join(output_dir, f"page_{i + 1}.jpg")
        image.save(image_path, "JPEG")
