import os
import poplib
import uuid
from dotenv import load_dotenv
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr
from aws_s3 import upload_file_to_s3
from pdf2image import convert_from_bytes
from io import BytesIO

load_dotenv()


# Function to decode email header
def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        value = value.decode(charset)
    return value


# Connect to Gmail POP3 server
pop_conn = poplib.POP3_SSL('pop.gmail.com')
pop_conn.user(os.getenv("EMAIL"))  # Provide full email address as username
pop_conn.pass_(os.getenv("APP_PASSWORD"))


def read_email_data():
    try:
        # Get messages from server
        message_count = len(pop_conn.list()[1])
        if message_count == 0:
            return None

        # Process only the first email
        i = 1
        # Retrieve message by ID
        resp, lines, octets = pop_conn.retr(i)
        # Concatenate lines into single message
        msg_content = b'\n'.join(lines).decode('utf-8')
        # Parse message into an email object
        msg = Parser().parsestr(msg_content)
        # Extract subject
        subject = decode_str(msg['Subject'])
        print("Subject:", subject)
        # Extract sender
        sender = decode_str(parseaddr(msg.get('From'))[1])
        print("From:", sender)
        submission_id = str(uuid.uuid4())

        # Extract and print email body
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get('Content-Disposition'))
            # Check if it's an attachment
            if content_disposition and content_disposition.startswith('attachment'):
                # Extract attachment filename
                filename = decode_str(part.get_filename())
                # Save attachment
                if filename:
                    print("Attachment:", filename)
                    file_content = part.get_payload(decode=True)
                    if filename.lower().endswith('.pdf') and 'acord' in filename.lower():
                        # Convert PDF to images
                        images = convert_from_bytes(file_content)
                        file = filename.split('.')[0]
                        for page_num, image in enumerate(images):
                            image_filename = f"{file}_page_{page_num + 1}.png"
                            # Save the image to a bytes buffer
                            buffer = BytesIO()
                            image.save(buffer, format='PNG')
                            buffer.seek(0)
                            # Upload image to S3
                            url = upload_file_to_s3(submission_id=submission_id,
                                                    filename=file + "/" + image_filename,
                                                    content=buffer.read())
                            print(f"Uploaded {image_filename} to {url}")
                    else:
                        url = upload_file_to_s3(submission_id=submission_id, filename=filename, content=file_content)
                        print(url)

        pop_conn.quit()
        return submission_id

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

