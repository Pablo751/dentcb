import io
import streamlit as st
import csv
from openai import OpenAI
import difflib
import os

# Set your OpenAI API key as an environment variable named 'OPENAI_API_KEY'
openai_api_key = os.environ['OPENAI_API_KEY']

# Instantiate the client
client = OpenAI()

# Define the CSV files based on country selection
csv_files = {
    'France': 'Dentaly URLS - Dentaly FR.csv',
    'US': 'Dentaly URLS - Dentaly US.csv',
    'UK': 'Dentaly URLS - Dentaly UK.csv',
    'Germany': 'Dentaly URLS - Dentaly DE.csv',
    'Spain': 'Dentaly URLS - Dentaly ES.csv',
    'Italy': 'Dentaly URLS - DD.csv',
}

# Initialize or reset session state if needed
if 'data_loaded' not in st.session_state or 'data' not in st.session_state:
    st.session_state['data_loaded'] = False
    st.session_state['data'] = None

# Streamlit interface for selecting country
st.title("Dentaly chatbot prototype")
country_choice = st.selectbox("Please select a country:", options=list(csv_files.keys()))
csv_file_path = csv_files.get(country_choice)

# Prompt the user for their question via Streamlit
question = st.text_input("Please enter your question:")

# Load and cache data based on the selected country
def load_data(csv_file_path):
    if not st.session_state['data_loaded'] or st.session_state['csv_file_path'] != csv_file_path:
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            st.session_state['data'] = list(reader)  # Read the entire CSV file into a list
        st.session_state['data_loaded'] = True
        st.session_state['csv_file_path'] = csv_file_path

# Ensure data is loaded appropriately
if csv_file_path:
    load_data(csv_file_path)

# Function to extract the main keywords using the GPT model
def extract_main_keywords(question):
    prompt = f"What are the main keyword or keywords of this question: '{question}'. Only choose one keyword, the most relevant to dental topics."
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}]
    )
    main_keywords = response.choices[0].message.content.strip().lower().split(', ')
    main_keywords = [kw.strip("'\"") for kw in main_keywords]
    return set(main_keywords)

# Function definitions (count_keyword_matches_script1, count_keyword_matches_script2, find_best_match, choose_best_url, provide_detailed_answer) remain unchanged

# Main Streamlit execution when 'Find Best Match' button is pressed
if st.button("Find Best Match"):
    if not question or not csv_file_path:
        st.write("Please make sure to select a country and enter a question.")
    else:
        scored_urls = find_best_match(question, st.session_state['data'])
        final_url = choose_best_url(question, scored_urls)
        if final_url:
            st.write("Chosen URL:", final_url)
            detailed_answer = provide_detailed_answer(question, final_url, st.session_state['data'])
            st.write("Detailed Answer:", detailed_answer)
        else:
            st.write("No URL could be selected based on the question.")
