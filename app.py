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
question = st.text_input("Please enter your question:").strip()

# Load and cache data based on the selected country
def load_data(csv_file_path):
    if not st.session_state['data_loaded'] or st.session_state['csv_file_path'] != csv_file_path:
        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                data = list(reader)  # Read the entire CSV file into a list
            st.session_state['data'] = data
            st.session_state['data_loaded'] = True
            st.session_state['csv_file_path'] = csv_file_path
            print(f"Data loaded successfully from {csv_file_path}")
            return data
        except FileNotFoundError:
            st.error(f"File not found: {csv_file_path}")
            st.session_state['data_loaded'] = False
            st.session_state['data'] = None
            return None
    else:
        print(f"Data already loaded from {csv_file_path}")
        return st.session_state['data']

# Function to extract the main keywords using the GPT model
def extract_main_keywords(question):
    prompt = f"What are the main keyword or keywords of this question: '{question}'. Only choose one keyword, the most relevant to dental topics. For example, lets say you identify ['brosse à dents en bambou', 'efficace'], in this case, you should only select at the end 'brosse à dents en bambou'"
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}]
    )
    main_keywords = response.choices[0].message.content.strip().lower().split(', ')
    main_keywords = [kw.strip("'\"") for kw in main_keywords]
    return set(main_keywords)

# Function to count keyword matches in the top_queries and score them
def count_keyword_matches_script1(row, main_keywords):
    top_queries = set(row['top_queries'].lower().split(', '))
    title = set(row['title'].lower().split(' '))
    meta = set(row['meta'].lower().split(' '))
    url = set(row['url'].lower().replace('-', ' ').split(' '))
    exact_match_score = 3
    partial_match_score = 1
    score = 0
    
    def score_matches(field_set, multiplier=1):
        field_score = 0
        for field_item in field_set:
            if any(kw in field_item for kw in main_keywords):
                field_score += partial_match_score * multiplier
            if any(kw == field_item for kw in main_keywords):
                field_score += (exact_match_score - partial_match_score) * multiplier
        return field_score

    score += score_matches(top_queries)
    score += score_matches(title, 2)
    score += score_matches(meta, 2)
    score += score_matches(url, 2)

    return score, row['url']
    
def count_keyword_matches_script2(row, main_keywords):
    top_queries = row['top_queries'].lower().split(', ')
    title = row['title'].lower().split(' ')
    meta = row['meta'].lower().split(' ')
    url = row['url'].lower().replace('-', ' ').split(' ')
    score = 0
    similarity_threshold = 0.6

    def score_based_on_similarity(field_list, multiplier=1):
        field_score = 0
        for field_item in field_list:
            for kw in main_keywords:
                if difflib.SequenceMatcher(None, kw, field_item).ratio() > similarity_threshold:
                    field_score += 3 * multiplier
        return field_score

    score += score_based_on_similarity(top_queries)
    score += score_based_on_similarity(title, 2)
    score += score_based_on_similarity(meta, 2)
    score += score_based_on_similarity(url, 2)

    return score, row['url']

def find_best_match(question, data):
    main_keywords = extract_main_keywords(question)
    print(f"Selected main keywords: {main_keywords}")  # Print the selected main keywords
    scored_urls = []
    
    for row in data:
        score, url = count_keyword_matches_script1(row, main_keywords)
        if score > 0:
            scored_urls.append((score, row['url'], row['title'], row['meta']))
    
    if not scored_urls:  # If no matches found, use second script
        for row in data:
            score, url = count_keyword_matches_script2(row, main_keywords)
            if score > 0:
                scored_urls.append((score, row['url'], row['title'], row['meta']))

    return scored_urls

def choose_best_url(question, scored_urls):
    if not scored_urls:
        return None

    prompt = f"Question: {question}\n\n"
    prompt += "Here are the possible answers based on relevance:\n"
    for idx, (score, url, title, meta) in enumerate(scored_urls, 1):
        prompt += f"{idx}. URL: {url}, Title: {title}, Meta: {meta}\n"

    prompt += "\nWhich URL is the most appropriate for the question? Please provide the URL only."

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}]
    )

    chosen_url = response.choices[0].message.content.strip()
    return chosen_url

def provide_detailed_answer(question, final_url, data):
    if not final_url:
        return "No URL was chosen for the question."

    normalized_final_url = final_url.strip().lower()
    page_detail = next((row['Page Detail'] for row in data if row['url'].strip().lower() == normalized_final_url), None)
    
    # Debugging: Print all URLs to see if there's a matching issue
    for row in data:
        print(f"Checking URL: {row['url'].strip().lower()}")

    if not page_detail:
        print(f"No page detail found for URL: {normalized_final_url}")
        return "No additional details found for the selected URL."

    prompt = f"Question: {question}\n\n"
    prompt += f"Selected URL: {final_url}\n\n"
    prompt += f"Page Detail: {page_detail}\n\n"
    prompt += "Based on the Page Detail information, provide a comprehensive answer to the question. Always answer in the content original language."
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "system", "content": prompt}]
    )

    detailed_answer = response.choices[0].message.content.strip()
    detailed_answer += f" [1{{{final_url}}}]"  # Append the source URL
    return detailed_answer

def recommend_related_content(scored_urls, exclude_url, count=2):
    related_content = [(score, url, title) for score, url, title, meta in scored_urls if url != exclude_url]
    return related_content[:count]

# Main execution when 'Find Best Match' button is pressed
if st.button("Find Best Match"):
    if not question or not csv_file_path:
        st.write("Please make sure to select a country and enter a question.")
    else:
        # Load the data
        data = load_data(csv_file_path)
        
        # Check if data is loaded successfully
        if st.session_state['data_loaded'] and st.session_state['data']:
            scored_urls = find_best_match(question, st.session_state['data'])
            final_url = choose_best_url(question, scored_urls)
            if final_url:
                st.write("Chosen URL:", final_url)
                detailed_answer = provide_detailed_answer(question, final_url, st.session_state['data'])
                st.write("Detailed Answer:", detailed_answer)
                
                # Recommend related content
                related_content = recommend_related_content(scored_urls, final_url)
                if related_content:
                    st.write("Recommended related content URLs:")
                    for idx, (score, url, title) in enumerate(related_content, start=2):  # Start indexing from 2 for related content
                        st.write(f"[{idx}{{{url}}}] Title: {title}")
                else:
                    st.write("No related content found.")
            else:
                st.write("No URL could be selected based on the question.")
        else:
            st.write("Failed to load data. Please check the CSV file path.")
