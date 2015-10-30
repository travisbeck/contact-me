from bottle import Bottle, request, response, redirect
from email.mime.text import MIMEText
import base64
import httplib2
import oauth2client
from apiclient import discovery
from validate_email_address import validate_email
import logging
import logging.handlers
import os
import requests

LOG_FILENAME = 'contact-me.log'
LOG_PATH = os.path.join(os.getcwd(), LOG_FILENAME)
DOMAIN = 'brontosaurus.net'
RECIPIENT = 'travis@brontosaurus.net'
GMAIL_USERNAME = 'travis@brontosaurus.net'
RECAPTCHA_SITE_KEY = '6Ldq1g8TAAAAAK4E_wD7tLLydYP2OvLhjbsbcAcx'
RECAPTCHA_SECRET = '6Ldq1g8TAAAAAKseL30KSHc8WCGmlZlrwX9vyWS2'

# set up logging
LOGGER = logging.getLogger('contact-me')
LOGGER.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.handlers.RotatingFileHandler(
            LOG_FILENAME, maxBytes=1000000, backupCount=5)
handler.setFormatter(formatter)
LOGGER.addHandler(handler)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
LOGGER.addHandler(console)

app = Bottle()

def send_mail(recipient, sender, name, message):
    msg = MIMEText(message)

    msg['Subject'] = '[%s] Contact form submission by %s' % (DOMAIN, name)
    msg['From'] = sender
    msg['Reply-To'] = sender
    msg['To'] = recipient

    LOGGER.info(msg.as_string())

    encoded_message = {'raw': base64.urlsafe_b64encode(msg.as_string())}

    credential_path = os.path.join(os.getcwd(), 'credentials.json')
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        raise Exception('Invalid credentials - rerun authorize.py')

    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    try:
        sent_message = (service.users().messages().send(userId=GMAIL_USERNAME, body=encoded_message)
                .execute())
        LOGGER.info('Message sent - ID: %s' % sent_message['id'])
        return sent_message
    except errors.HttpError, error:
        LOGGER.error('No message sent - Error: %s' % error)

@app.get('/ip')
def ip():
    response.content_type = 'text/plain'
    return request.remote_addr + '\n'

@app.post('/contact')
def contact():
    try:
        email = request.POST.get("email", "").strip()
        name = request.POST.get("name", "").strip()
        message = request.POST.get("message", "").strip()
        recaptcha_response = request.POST.get("g-recaptcha-response", "").strip()
        LOGGER.info('Received form:\nemail: %s\nname: %s\nip: %s\nmessage: %s'
                    % (email, name, request.remote_addr, message))

        if not email:
            raise Exception('Missing email')
        elif not name:
            raise Exception('Missing name')
        elif not message:
            raise Exception('Missing message')
        elif not validate_email(email):
            raise Exception('Invalid email address')
        else:
            recaptcha_data = { 'secret': RECAPTCHA_SECRET,
                               'response': recaptcha_response,
                               'remoteip': request.remote_addr }
            verify_response = requests.post('https://www.google.com/recaptcha/api/siteverify',
                                            data=recaptcha_data)

            if not verify_response or not verify_response.json().success:
                LOGGER.info('recaptcha response %s' % verify_response.text)
                raise Exception('Recaptcha fail')
            else:
                send_mail(RECIPIENT, email, name, message);
    except Exception, e:
        LOGGER.error(e.message)
        LOGGER.info('no email sent')
        return redirect("/#whoops")

    return redirect("/#thanks")

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
