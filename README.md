# Sentiment and Readability Analysis System

This project is a Python-based tool that extracts article content from URLs and performs sentiment analysis and readability metrics calculation. The tool scrapes articles using web scraping techniques, processes the text for linguistic analysis, and generates detailed reports in Excel format.

## Features

- **Web Scraping**: Extracts content from provided URLs, including headings, paragraphs, and lists.
- **Sentiment Analysis**: Calculates sentiment scores (positive, negative, polarity, and subjectivity) using custom word dictionaries.
- **Readability Metrics**: Computes FOG index, average sentence length, percentage of complex words, and syllables per word.
- **Text Statistics**: Counts personal pronouns, computes average word length, and performs detailed word tokenization.
- **Batch Processing**: Handles large datasets and saves each article as a text file while outputting analysis results in Excel format.

## Tech Stack

- **Python**: Core programming language
- **BeautifulSoup**: Web scraping
- **NLTK**: Natural Language Processing, tokenization, and stopword filtering
- **Pandas**: Data manipulation and report generation
- **Excel**: Output format for analyzed data

## Setup Instructions

### Requirements

- Python 3.6+
- `shell.nix` provided for easy environment setup with `nix-shell`

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/Sentiment-Readability-Analysis.git
    cd Sentiment-Readability-Analysis
    ```

2. Enter the development environment:
    ```bash
    nix-shell
    ```

### Directory Structure

```bash
.
├── MasterDictionary
│   ├── positive-words.txt
│   ├── negative-words.txt
├── StopWords
│   ├── stopword1.txt
│   ├── stopword2.txt
├── articles
├── Input.xlsx
├── Output Data Structure.xlsx
├── main.py
├── README.md
└── shell.nix
```

- `MasterDictionary/`: Contains positive and negative word dictionaries.
- `StopWords/`: Folder for custom stopword lists.
- `articles/`: Directory where extracted article texts are saved.
- `Input.xlsx`: Excel file containing article URLs.
- `Output Data Structure.xlsx`: Generated Excel file containing sentiment and readability metrics.

### Usage

1. Add the URLs for articles to be analyzed in `Input.xlsx` under the columns `URL_ID` and `URL`.
2. Run the main script:
    ```bash
    python main.py
    ```
3. The results will be saved in `Output Data Structure.xlsx`, and each article's content will be stored in the `articles/` directory.

### Output

The tool outputs an Excel file with the following metrics:

- Positive Score
- Negative Score
- Polarity Score
- Subjectivity Score
- Average Sentence Length
- Percentage of Complex Words
- FOG Index
- Word Count
- Syllables Per Word
- Personal Pronouns Count
- Average Word Length

---
