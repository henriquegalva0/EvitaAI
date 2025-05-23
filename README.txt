Hi! This is a group Project made by our team EvitaAI.
The goal of the application is creating a virtual plataform for detecting phishing or malwares disguised in URLs or emails using AI. Our main plan is to make this democratic, so as we will present this to big enterprises in order to help people achieve their goals without worrying about data stealing.

All the frameworks used in our project can be downloaded in the terminal after creating a virtual environment in python

  pip install openai
  pip install flask
  pip install google-auth google-auth-oauthlib google-api-python-client

There are 5 files we didn't publish here.

  # credentials.json
This file contains the parameters that the google API reads to enable accessing emails.

  # promtgptemail.txt & promtgptsite.txt
Both files contains our promts to return well structreds responses. Then we treat the strings and display them on the screen.
The template used is: topic1:Trustful or Malicious \n/////\n topic2:Info about the email's author or the site's host \n/////\n topic3:Info about the AI's judgement \n/////\n topic4:Security tips and recommendations

  # apikeychatgpt.txt
This file contains the secret key for the openai API

  # appkey.txt
This file contains the secret key for the flask APP
