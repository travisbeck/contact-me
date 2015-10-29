from bottle import Bottle, request, redirect
import smtplib
from email.mime.text import MIMEText
from validate_email_address import validate_email
import logging
import logging.handlers
import os

LOG_FILENAME = 'contact-me.log'
LOG_PATH = os.path.join(os.getcwd(), LOG_FILENAME)
DOMAIN = 'brontosaurus.net'
RECIPIENT = 'travis@brontosaurus.net'
GMAIL_USERNAME = 'travis@brontosaurus.net'
GMAIL_APP_PASSWORD = 'wmpcueqdfqidtnar'
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

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(GMAIL_USERNAME, GMAIL_APP_PASSWORD)
    server.sendmail(sender, recipient, msg.as_string())
    server.quit()

@app.post('/contact')
def contact():
    try:
        email = request.POST.get("email", "").strip()
        name = request.POST.get("name", "").strip()
        message = request.POST.get("message", "").strip()
        LOGGER.info('Recieved:\nemail: %s\nname: %s\nip: %s\nmessage: %s'
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
            send_mail(RECIPIENT, email, name, message);
            LOGGER.info('email sent')
    except Exception, e:
        LOGGER.error(e.message)
        LOGGER.info('no email sent')
        return redirect("/#whoops")

    return redirect("/#thanks")

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
