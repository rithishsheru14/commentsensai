from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from flask import Flask, render_template, request
import googleapiclient.discovery
import pandas as pd
from nltk.corpus import stopwords
from textblob import TextBlob
import google.generativeai as palm
from flask import Flask, render_template, request, jsonify
from flask import Flask, render_template, request
import googleapiclient.discovery
import pandas as pd
from nltk.corpus import stopwords
from textblob import TextBlob
from transformers import pipeline
from googletrans import Translator
import time
import google.generativeai as palm
from translate import Translator
from langdetect import detect


app = Flask(__name__)
app.secret_key = 'your_secret_key'  





 Function to preprocess text
def preprocess_text(text):
    words = text.lower().split()
    words = [word for word in words if word.isalnum() and word not in stop_words]
    return " ".join(words)

# Function for TextBlob sentiment analysis (multilingual)
def analyze_sentiment_textblob(comment):
    analysis = TextBlob(comment)
    return analysis.sentiment.polarity

# Function to translate text
def translate_text(text, target_lang):
    # Detect the source language
    source_lang = detect(text)

    # Translate text
    translator = Translator(to_lang=target_lang, from_lang=source_lang)
    translated_text = translator.translate(text)

    return translated_text

# Initialize YouTube API
api_service_name = "youtube"
api_version = "v3"
DEVELOPER_KEY = "YOUR_DEVELOPER_KEY"
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey="AIzaSyDDTnTK_4V3-nH1BGxsPWqeg-WYrTHJspM")

# Preprocess text
stop_words = set(stopwords.words("english"))

# Route to handle the web request
@app.route('/getsuggestions', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        video_id = request.form.get('video_id')

        # Fetch YouTube comments
        request_youtube = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100
        )
        response = request_youtube.execute()

        # Extract comments
        comments = [item['snippet']['topLevelComment']['snippet']['textDisplay'] for item in response['items']]

        # Analyze sentiment for each comment
        df = pd.DataFrame(comments, columns=['comment'])
        df["clean_comment"] = df["comment"].apply(preprocess_text)

        # Analyze sentiment for each comment
        df["sentiment_score"] = df["clean_comment"].apply(analyze_sentiment_textblob)

        top_positive_comments = df.nlargest(20, "sentiment_score")
        top_negative_comments = df.nsmallest(20, "sentiment_score")

        # Combine top comments into strings
        combined_positive_comments = " ".join(top_positive_comments['comment'])
        combined_negative_comments = " ".join(top_negative_comments['comment'])

        # Translate comments to English
        combined_positive_comments = translate_text(combined_positive_comments, "en")
        combined_negative_comments = translate_text(combined_negative_comments, "en")

        # Summarize the top positive and negative comments
        summarizer = pipeline("summarization")
        positive_summary = summarizer(combined_positive_comments)
        negative_summary = summarizer(combined_negative_comments)

        palm.configure(api_key='AIzaSyDo8N-OVBQWFeVy8VIzUW9q261HueN9xeo')
        models = [m for m in palm.list_models() if 'generateText' in m.supported_generation_methods]
        model = models[0].name

        positive_summary_text = positive_summary[0]['summary_text']
        negative_summary_text = negative_summary[0]['summary_text']

        prompt = f"Give me suggestions to improve my YouTube content. Here are summaries of the top comments:\n\nPositive Summary: {positive_summary_text}\n\nNegative Summary: {negative_summary_text}"

        # Adjust temperature as needed
        completion = palm.generate_text(
            model=model,
            prompt=prompt,
            temperature=0.8,  # Adjust as needed
            max_output_tokens=800,
        )

        result = {
            "positive_summary": positive_summary_text,
            "negative_summary": negative_summary_text,
            'suggestions': completion.result,
        }

        return render_template('result.html', result=result)

    return render_template('index.html')


def preprocess_text(text):
    words = text.lower().split()
    words = [word for word in words if word.isalnum() and word not in stop_words]
    return " ".join(words)

# Function for TextBlob sentiment analysis (multilingual)
def analyze_sentiment_textblob(comment):
    analysis = TextBlob(comment)
    return analysis.sentiment.polarity
# App 1: Home Page
@app.route('/')
def home():
    return render_template('home-page-laptop.html')

# App 2: About Page
@app.route('/about')
def about():
    return render_template('index.html')
@app.route('/dashboard')
def dashboard():
    return render_template('path.html')

# App 3: Contact Page
@app.route('/contact')
def contact():
    return render_template('login-page-laptop.html')
@app.route('/register', methods=['POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['firstName']
        last_name = request.form['lastName']
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Check if the email is unique
        cursor.execute("SELECT email FROM users WHERE email = ?", (email,))
        existing_email = cursor.fetchone()

        if existing_email:
            return 'Email already in use'

        # Check if the name is unique
        cursor.execute("SELECT first_name, last_name FROM users WHERE first_name = ? AND last_name = ?", (first_name, last_name))
        existing_name = cursor.fetchone()

        if existing_name:
            return 'Name already in use'

        # Insert user data into the database
        cursor.execute("INSERT INTO users (first_name, last_name, email, password) VALUES (?, ?, ?, ?)",
                       (first_name, last_name, email, password))

        conn.commit()
        conn.close()

        # For demonstration purposes, you can redirect to a "registration successful" page
        return render_template('login-page-laptop.html')

    return 'Invalid request'
@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        # Query the database to fetch the user by email and password
        cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            # User is authenticated; store user information in a session
            session['user_id'] = user[0]
            return render_template('path.html')  # Replace 'dashboard' with the desired page
        else:
            return 'Login failed'

    return 'Invalid request'

if __name__ == '__main__':
    app.run(debug=True)
