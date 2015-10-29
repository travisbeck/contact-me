import smtplib
from email.mime.text import MIMEText

DOMAIN = 'brontosaurus.net'
GMAIL_USERNAME = 'travis@brontosaurus.net'
GMAIL_APP_PASSWORD = 'wmpcueqdfqidtnar'

def send_mail(recipient, sender, name, message):
    msg = MIMEText(message)

    msg['Subject'] = '[%s] Contact form submission by %s' % (DOMAIN, name)
    msg['From'] = sender
    msg['To'] = recipient

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(GMAIL_USERNAME, GMAIL_APP_PASSWORD)
    server.sendmail(sender, recipient, msg.as_string())
    server.quit()

send_mail('travis@brontosaurus.net', 'travis.beck@gmail.com', 'Travis Beck', 'This is another test');
