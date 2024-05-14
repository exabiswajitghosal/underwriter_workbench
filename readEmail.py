import os
import email
import poplib
from dotenv import load_dotenv
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr

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

print("EMAIL EXTRACT")

# Get messages from server
message_count = len(pop_conn.list()[1])
for i in range(1, message_count + 1):
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

    # Extract and print email body
    for part in msg.walk():
        content_type = part.get_content_type()
        content_disposition = str(part.get('Content-Disposition'))
        print("Content-Type:", content_type)
        print("Content-Disposition:", content_disposition)
        # Check if it's an attachment
        if content_disposition and content_disposition.startswith('attachment'):
            # Extract attachment filename
            filename = decode_str(part.get_filename())
            # Save attachment
            if filename:
                print("Attachment:", filename)
                # Save attachment to current directory
                with open(filename, 'wb') as f:
                    f.write(part.get_payload(decode=True))
        elif content_type == 'text/plain' and 'attachment' not in content_disposition:
            body = part.get_payload(decode=True).decode('utf-8')
            print("Body:", body)

# Close connection
pop_conn.quit()
