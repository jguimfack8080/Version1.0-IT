import imaplib
import email
from email import policy
import re

user = 'coronaapp65@gmail.com'
password = 'hhne fbjj oqon gljp'
host = 'imap.gmail.com'

# Connect securely with SSL
imap = imaplib.IMAP4_SSL(host)

## Login to remote server
imap.login(user, password)

imap.select('inbox')

# Variable pour suivre si un e-mail correspondant a été trouvé
email_trouve = False

# Recherche les e-mails dans l'ordre inverse de leur date pour récupérer le plus récent en premier
tmp, messages = imap.search(None, 'ALL')
messages = messages[0].split()[::-1]  # Inverser l'ordre de la liste des numéros de messages

for num in messages:
    # Retrieve email message by ID
    tmp, data = imap.fetch(num, '(RFC822)')
    raw_email = data[0][1]
    
    # Parse raw email
    msg = email.message_from_bytes(raw_email, policy=policy.default)

    # Check for the presence of 'Re: [ACME-PGP] Response' in email subject
    if msg['Subject'] == 'Re: [ACME-PGP] Response':
        # Initialize payload
        payload = ""
        # Walk through the message and get text from all parts
        for part in msg.walk():
            # Check if current part is text/plain
            if part.get_content_type() == 'text/plain':
                # Decode payload if necessary and append to payload variable
                payload += part.get_payload(decode=True).decode()
        # Find 'Challenge-token' string in email payload
        match = re.search(r'Challenge-token: "(.*?)"', payload)
        if match:
            token_value = match.group(1)
            print('Token value:', token_value)
            email_trouve = True
            break

# Si aucun e-mail correspondant a été trouvé, afficher un message
if not email_trouve:
    print("Aucun token trouvé.")

imap.close()
imap.logout()
