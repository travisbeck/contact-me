from email.mime.text import MIMEText
import base64
import httplib2
import oauth2client
from apiclient import discovery
import os

DOMAIN = 'brontosaurus.net'

def send_mail(recipient, sender, name, message):
    msg = MIMEText(message)
    msg['Subject'] = '[%s] Contact form submission by %s' % (DOMAIN, name)
    msg['From'] = sender
    msg['To'] = recipient

    encoded_message = {'raw': base64.urlsafe_b64encode(msg.as_string())}

    credential_path = os.path.join(os.getcwd(), 'credentials.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    try:
        sent_message = (service.users().messages().send(userId='me', body=encoded_message)
                .execute())
        print 'Message Id: %s' % sent_message['id']
        return sent_message
    except errors.HttpError, error:
        print 'An error occurred: %s' % error

send_mail('travis@brontosaurus.net', 'travis.beck@gmail.com', 'Travis Beck', 'This is a new test');
