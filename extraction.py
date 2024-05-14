import csv
import zipfile
import os
import pdfplumber


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

