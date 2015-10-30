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
import json

config_path = os.path.join(os.getcwd(), 'config.json')

with open(config_path) as config_file:
    config = json.load(config_file)
    config['log_path'] = os.path.join(os.getcwd(), config['log_filename'])

# set up logging
logger = logging.getLogger('contact-me')
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.handlers.RotatingFileHandler(
            config['log_path'], maxBytes=1000000, backupCount=5)
handler.setFormatter(formatter)
logger.addHandler(handler)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(formatter)
logger.addHandler(console)

app = Bottle()

def send_mail(recipient, sender, name, message):
    msg = MIMEText(message)

    msg['Subject'] = '[%s] Contact request from %s' % (config['domain'], name)
    msg['From'] = sender
    msg['Reply-To'] = sender
    msg['To'] = recipient

    logger.info(msg.as_string())

    encoded_message = {'raw': base64.urlsafe_b64encode(msg.as_string())}

    credential_path = os.path.join(os.getcwd(), config['credentials_file'])
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        raise Exception('Invalid credentials - rerun authorize.py')

    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    try:
        sent_message = (service.users().messages().send(userId=config['gmail_username'], body=encoded_message)
                .execute())
        logger.info('Message sent - ID: %s' % sent_message['id'])
        return sent_message
    except errors.HttpError, error:
        logger.error('No message sent - Error: %s' % error)

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
        logger.info('Received form:\nemail: %s\nname: %s\nip: %s\nmessage: %s'
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
            recaptcha_data = { 'secret': config['recaptcha_secret'],
                               'response': recaptcha_response,
                               'remoteip': request.remote_addr }
            verify_response = requests.post('https://www.google.com/recaptcha/api/siteverify',
                                            data=recaptcha_data)

            data = verify_response.json()
            if not data or not data['success']:
                logger.info('recaptcha response %s' % verify_response.text)
                raise Exception('Recaptcha fail')
            else:
                send_mail(config['recipient'], email, name, message);
    except Exception, e:
        logger.error(e.message)
        logger.info('no email sent')
        if e.message == 'Recaptcha fail':
            return redirect('/')
        else:
            return redirect("/#whoops")

    return redirect("/#thanks")

if __name__ == '__main__':
    app.debug = True
    app.run(port=5000)
