# contact-me
Super simple contact submission form app for my personal website

### Setup GMail API access

On the google developers console (https://console.developers.google.com):

1. Enable the Gmail API
2. Add an OAuth2 client with an application type of 'Other'
3. Click the 'Download JSON' button
4. Rename the file 'client_secret.json' and add it to your project
5. On your local machine (somewhere that can load a web page), run

 python authorize.py

6. Update 'config.json' with your information
7. Run the app

 python app.py

8. Deploy!
