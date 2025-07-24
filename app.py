from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from utils.speech_to_text import recognize_speech
from utils.text_to_speech import speak_text
from utils.email_sender import send_email
from utils.email_reader import fetch_emails
from flask import jsonify
from gtts import gTTS
import pyglet
import time

app = Flask(__name__)
app.secret_key = '1234'

# Dummy login credentials
USER_EMAIL = 'manasa@gmail.com'
USER_PASSWORD = '12345'

def speak_text(text):
    try:
        filename = "static/audio/temp.mp3"
        tts = gTTS(text=text, lang='en')
        tts.save(filename)

        music = pyglet.media.load(filename, streaming=False)
        music.play()
        time.sleep(music.duration + 0.5)

        if os.path.exists(filename):
            os.remove(filename)
    except Exception as e:
        print("Error in speak_text:", e)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == USER_EMAIL and password == USER_PASSWORD:
            session['email'] = email
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials')
    else:
        speak_text("Welcome. Speak your email and password, then say login to continue.")
    return render_template('login.html')




@app.route('/dashboard')
def dashboard():
    if 'email' not in session:
        return redirect(url_for('login'))
    speak_text("You are on the dashboard. Say 'compose' to write a new email, 'inbox' to check your emails, or 'logout' to sign out.")
    return render_template('dashboard.html')

@app.route('/compose', methods=['GET', 'POST'])
def compose():
    if 'email' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        to = request.form['to']
        subject = request.form['subject']
        body = request.form['body']
        send_email(USER_EMAIL, USER_PASSWORD, to, subject, body)
        flash('Email sent successfully')
        return redirect(url_for('dashboard'))
    speak_text("Compose your email. Say the recipient email, subject, and then the message. Then say 'send' to send the email.")
    return render_template('compose.html')

@app.route('/inbox')
def inbox():
    if 'email' not in session:
        return redirect(url_for('login'))
    emails = fetch_emails(USER_EMAIL, USER_PASSWORD)
    speak_text("Here are your latest emails. Say 'back' to return to the dashboard or 'logout' to exit.")
    return render_template('inbox.html', emails=emails)

@app.route('/logout')
def logout():
    session.pop('email', None)
    speak_text("You have been logged out. Goodbye.")
    return redirect(url_for('login'))


@app.route('/record/<field>')
def record(field):
    text = recognize_speech()
    if text:
        # Normalize spoken email syntax
        text = text.lower().replace(" at ", "@").replace(" dot ", ".").replace(" underscore ", "_")
        text = text.replace(" ", "")  # Remove spaces in email/password
    return jsonify({'text': text})


if __name__ == '__main__':
    os.makedirs('static/audio', exist_ok=True)
    app.run(debug=True)