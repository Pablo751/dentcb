
# Dentaly Keyword Matching Script

This script processes a given URL and a question to find the most relevant Dentaly URL based on keyword matching and similarity scoring. It leverages OpenAI's GPT model for extracting main keywords and generating responses.

## Prerequisites

- Python 3.6+
- OpenAI Python client library
- CSV files containing Dentaly URLs and their associated data

## Installation

1. Clone the repository or download the script.
2. Install the required Python packages:

    ```bash
    pip install openai
    ```

3. Set your OpenAI API key as an environment variable:

    ```bash
    export OPENAI_API_KEY='your_openai_api_key'
    ```

## Script Explanation

### Imports

The script imports several modules:
- `csv` for handling CSV file operations
- `os` for environment variable access
- `OpenAI` for interacting with the OpenAI API
- `difflib` for sequence matching
- `urllib.parse` for URL parsing

### Configuration

- `openai_api_key`: Retrieves the OpenAI API key from environment variables.
- `client`: Instantiates the OpenAI client.
- `csv_files`: Dictionary mapping countries to their respective CSV files.
- `country_languages`: Dictionary mapping countries to their languages.

### Functions

1. **`get_country_from_url(url)`**:
   Extracts the country from a given URL based on its path.

2. **`load_data(csv_file_path)`**:
   Loads and caches data from a specified CSV file.

3. **`extract_main_keywords(question)`**:
   Uses the GPT model to extract the main keywords from a question.

4. **`count_keyword_matches_script1(row, main_keywords)`**:
   Scores keyword matches in the CSV data using exact and partial matching.

5. **`count_keyword_matches_script2(row, main_keywords)`**:
   Scores keyword matches based on similarity using the `difflib` library.

6. **`find_best_match(question, data)`**:
   Finds the best matching URLs for a given question by scoring keyword matches.

7. **`choose_best_url(question, scored_urls)`**:
   Prompts the GPT model to choose the most appropriate URL based on the scored matches.

8. **`provide_detailed_answer(question, final_url, data, language)`**:
   Provides a detailed answer based on the selected URL and the question.

9. **`recommend_related_content(scored_urls, exclude_url, count=2)`**:
   Recommends related content URLs excluding the chosen URL.

10. **`main(url, question)`**:
    Main execution function that integrates all the above functions.

### Usage

To run the script, execute the following command in your terminal:

```bash
python script_name.py
```

Replace `script_name.py` with the name of your script file. The script will prompt you for a URL and a question, and then it will process the input to find and recommend the most relevant Dentaly URLs.

### Example Usage

You can also use the `main` function directly by passing a test URL and question:

```python
if __name__ == "__main__":
    test_url = "https://www.dentaly.org/en/"
    test_question = "What are the benefits of dental implants?"
    main(test_url, test_question)
```

## Notes

- Ensure that the CSV files are in the correct format and located in the same directory as the script.
- The script relies on the OpenAI API for keyword extraction and response generation, so an active internet connection is required.

## License

This project is licensed under the MIT License.
