import streamlit as st
import csv
from openai import OpenAI
import difflib
import io
import os

# Set your OpenAI API key as an environment variable named 'OPENAI_API_KEY'
openai_api_key = os.environ['OPENAI_API_KEY']

# Instantiate the client
client = OpenAI()

# Function to extract the main keywords using the GPT model
def extract_main_keywords(question):
    prompt = f"What are the main keyword or keywords of this question: '{question}'? List them separated by commas."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}]
    )
    main_keywords = response.choices[0].message.content.strip().lower().split(', ')
    return set(main_keywords)

# Function to count keyword matches in the top_queries and score them
def count_keyword_matches_script1(row, main_keywords):
    top_queries = set(row['top_queries'].lower().split(', '))
    exact_match_score = 3 # Score for exact matches
    partial_match_score = 1 # Score for partial matches
    score = 0
    for kw in main_keywords:
        if kw in top_queries:
            score += exact_match_score  # Exact match
        else:
            # Check for partial matches (if any keyword partially matches the top queries)
            for query in top_queries:
                if kw in query:
                    score += partial_match_score
                    break
    return score, row['url']

def count_keyword_matches_script2(row, main_keywords):
    top_queries = row['top_queries'].lower().split(', ')
    score = 0
    similarity_threshold = 0.6 # Consider a match if similarity is above 70%
    for kw in main_keywords:
        for query in top_queries:
            if difflib.SequenceMatcher(None, kw, query).ratio() > similarity_threshold:
                score += 3 # Assign a score for each good match
    return score, row['url']

# Streamlit interface
st.title("Dentaly chatbot prototype (FR)")
question = st.text_input("Please enter your query:")

# Load the CSV file from the same directory as the script
with open('FRdata.csv', mode='r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    if st.button("Submit"):
        main_keywords = extract_main_keywords(question)
        st.write(f"Main Keywords Identified: {', '.join(main_keywords)}")
        highest_score = 0
        best_url = None
        for row in reader:
            score, url = count_keyword_matches_script1(row, main_keywords)
            if score > highest_score:
                highest_score = score
                best_url = url

        if best_url:
            st.write(f"URL with highest score: {best_url}")
        else:
            st.write("No matches found. Using second script logic...")
            highest_score = 0
            best_url = None
            for row in reader:
                score, url = count_keyword_matches_script2(row, main_keywords)
                if score > highest_score:
                    highest_score = score
                    best_url = url
            if best_url:
                st.write(f"URL with highest score: {best_url}")
            else:
                st.write("No matches found.")
