from flask import Flask, request, jsonify
import google.generativeai as genai  # Using Gemini for NLP
import psycopg2  # Using PostgreSQL for NeonDB
from bs4 import BeautifulSoup
import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Use variables
API_KEY = os.getenv("API_KEY")
DB_URL = os.getenv("DB_URL")
# Initialize Flask App
app = Flask(__name__)
from flask_cors import CORS
CORS(app)

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# Initialize PostgreSQL (NeonDB)
db_conn = psycopg2.connect(DB_URL)
db_cursor = db_conn.cursor()

# Function to scrape documentation
def scrape_docs(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
    return ""

# Preload documentation
DOCS = {
    "segment": scrape_docs("https://segment.com/docs/?ref=nav"),
    "mparticle": scrape_docs("https://docs.mparticle.com/"),
    "lytics": scrape_docs("https://docs.lytics.com/"),
    "zeotap": scrape_docs("https://docs.zeotap.com/home/en-us/")
}

# Function to store docs in NeonDB
def store_docs():
    for key, content in DOCS.items():
        db_cursor.execute("INSERT INTO cdp_docs (platform, content) VALUES (%s, %s) ON CONFLICT (platform) DO UPDATE SET content = EXCLUDED.content", (key, content))
    db_conn.commit()

# Function to query Gemini for answers
def get_answer(question):
    response = model.generate_content(question)
    return response.text if response else "Couldn't fetch an answer."

# API Endpoint to answer questions
@app.route("/ask", methods=["GET"])
def ask():
    question = request.args.get("q")
    if not question:
        return jsonify({"error": "No question provided."})
    
    # Check if it's a valid CDP question
    relevant_docs = [doc for key, doc in DOCS.items() if key in question.lower()]
    if not relevant_docs:
        return jsonify({"answer": "I only answer CDP-related questions."})
    
    # Query Gemini for response
    response = get_answer(question)
    return jsonify({"answer": response})

if __name__ == "__main__":
    store_docs()  # Store scraped docs into NeonDB
    app.run(debug=True)
