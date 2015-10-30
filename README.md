# contact-me
Super simple contact submission form app

I built this app for my personal website, and there isn't much to it, but it
does send through the Gmail API and enforces recaptcha. Let me know if this is
useful to you. Thanks!

### Setup

On the google developers console (https://console.developers.google.com):

1. Enable the Gmail API
2. Add an OAuth2 client with an application type of 'Other'
3. Click the 'Download JSON' button
4. Rename the file 'client_secret.json' and add it to your project
5. On your local machine (somewhere that can load a web page), run:

```
python authorize.py
```

6. Setup recaptcha through https://www.google.com/recaptcha/. Make note of your key and secret
7. Update 'config.json' with your information, including recaptcha secret
8. Setup virtualenv and install dependencies:

```
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

9. Run the app

```
python app.py
```

10. Deploy!
