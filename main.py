import pandas as pd
from bs4 import BeautifulSoup
import requests
import os
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
import re
import string

nltk.download('punkt', quiet=True)
nltk.download('stopwords', quiet=True)

def load_words(file_path):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return set(word.strip().lower() for word in f)

# Load dictionaries and stop words
positive_words = load_words('MasterDictionary/positive-words.txt')
negative_words = load_words('MasterDictionary/negative-words.txt')

stop_words = set()
for file in os.listdir('StopWords'):
    stop_words.update(load_words(f'StopWords/{file}'))

def extract_article(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract the title
    title_element = soup.find('h1', class_='entry-title')
    title = title_element.text.strip() if title_element else "No title found"

    # Extract the main content
    content_div = soup.find('div', class_='td-post-content tagdiv-type')
    if content_div:
        # Extract all relevant elements including paragraphs, headings, and lists
        content_elements = content_div.find_all(['p', 'h2', 'h3', 'h4', 'ul', 'ol'])
        
        formatted_content = []
        for element in content_elements:
            if element.name in ['h2', 'h3', 'h4']:
                # Add extra newlines before headings for clarity
                formatted_content.append(f"\n\n{element.text.strip()}\n")
            elif element.name in ['ul', 'ol']:
                # Format list items
                list_items = element.find_all('li')
                list_text = "\n".join(f"• {item.text.strip()}" for item in list_items)
                formatted_content.append(f"\n{list_text}\n")
            else:
                # Regular paragraphs
                formatted_content.append(element.text.strip())
        
        article_text = "\n\n".join(formatted_content)
    else:
        article_text = "No content found"

    # Clean up the text
    article_text = re.sub(r'\s+', ' ', article_text).strip()
    
    # Combine title and article text
    full_text = f"{title}\n\n{article_text}"
    
    # Basic check to ensure we've extracted meaningful content
    if len(full_text.split()) < 50:
        raise ValueError("Failed to extract meaningful content from the article.")

    return full_text

def clean_text(text):
    '''# Remove punctuation and convert to lowercase
    text = text.translate(str.maketrans('', '', string.punctuation)).lower()'''
    # Remove stopwords
    words = word_tokenize(text)
    return ' '.join([word for word in words if word not in stop_words])

def compute_sentiment_scores(text):
    words = word_tokenize(clean_text(text))
    positive_score = sum(1 for word in words if word in positive_words)
    negative_score = sum(1 for word in words if word in negative_words)
    negative_score *= -1  # Convert to positive number as per instructions
    
    total_words = len(words)
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (total_words + 0.000001)
    
    return positive_score, negative_score, polarity_score, subjectivity_score, total_words

def compute_readability_metrics(text):
    sentences = sent_tokenize(text)
    words = word_tokenize(clean_text(text))
    
    total_words = len(words)
    total_sentences = len(sentences)
    avg_sentence_length = total_words / total_sentences
    
    complex_words = [word for word in words if count_syllables(word) > 2]
    percentage_complex_words = len(complex_words) / total_words
    
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)
    
    return avg_sentence_length, percentage_complex_words, fog_index, len(complex_words), total_words, total_sentences

def count_syllables(word):
    word = word.lower()
    count = 0
    vowels = 'aeiouy'
    if word[0] in vowels:
        count += 1
    for index in range(1, len(word)):
        if word[index] in vowels and word[index - 1] not in vowels:
            count += 1
    if word.endswith('e'):
        count -= 1
    if word.endswith('le'):
        count += 1
    if count == 0:
        count += 1
    return count

def count_personal_pronouns(text):
    pronouns = r'\b(I|we|my|ours|us)\b'  # Regex pattern for personal pronouns
    # Exclude 'US' when it's not followed by a lowercase letter (to avoid counting the country name)
    matches = re.findall(pronouns, text, re.IGNORECASE)
    return len([m for m in matches if m.lower() != 'us' or (m.lower() == 'us' and not re.match(r'US\s+[a-z]', text[text.lower().index(m.lower()):]))])

def avg_word_length(text):
    words = word_tokenize(clean_text(text))
    return sum(len(word) for word in words) / len(words)

def analyze_text(text):
    cleaned_text = clean_text(text)
    pos_score, neg_score, polarity, subjectivity, total_words = compute_sentiment_scores(text)
    avg_sent_len, perc_complex, fog, complex_count, _, total_sentences = compute_readability_metrics(text)
    pronoun_count = count_personal_pronouns(text)
    avg_word_len = avg_word_length(text)
    
    syllable_per_word = sum(count_syllables(word) for word in word_tokenize(cleaned_text)) / total_words
    
    return {
        'POSITIVE SCORE': pos_score,
        'NEGATIVE SCORE': abs(neg_score),  
        'POLARITY SCORE': polarity,
        'SUBJECTIVITY SCORE': subjectivity,
        'AVG SENTENCE LENGTH': avg_sent_len,
        'PERCENTAGE OF COMPLEX WORDS': perc_complex,
        'FOG INDEX': fog,
        'AVG NUMBER OF WORDS PER SENTENCE': avg_sent_len,
        'COMPLEX WORD COUNT': complex_count,
        'WORD COUNT': total_words,
        'SYLLABLE PER WORD': syllable_per_word,
        'PERSONAL PRONOUNS': pronoun_count,
        'AVG WORD LENGTH': avg_word_len
    }

def main():
    df = pd.read_excel('Input.xlsx')
    os.makedirs('articles', exist_ok=True)
    
    results = []
    
    for index, row in df.iterrows():
        url_id = row['URL_ID']
        url = row['URL']
        
        try:
            article_text = extract_article(url)
            
            with open(f'articles/{url_id}.txt', 'w', encoding='utf-8') as f:
                f.write(article_text)
            
            print(f"Extracted and saved article {url_id}")
            
            analysis_results = analyze_text(article_text)
            
            # Create a dictionary with the exact order of columns
            result = {
                'URL_ID': url_id,
                'URL': url,
                'POSITIVE SCORE': analysis_results['POSITIVE SCORE'],
                'NEGATIVE SCORE': analysis_results['NEGATIVE SCORE'],
                'POLARITY SCORE': analysis_results['POLARITY SCORE'],
                'SUBJECTIVITY SCORE': analysis_results['SUBJECTIVITY SCORE'],
                'AVG SENTENCE LENGTH': analysis_results['AVG SENTENCE LENGTH'],
                'PERCENTAGE OF COMPLEX WORDS': analysis_results['PERCENTAGE OF COMPLEX WORDS'],
                'FOG INDEX': analysis_results['FOG INDEX'],
                'AVG NUMBER OF WORDS PER SENTENCE': analysis_results['AVG NUMBER OF WORDS PER SENTENCE'],
                'COMPLEX WORD COUNT': analysis_results['COMPLEX WORD COUNT'],
                'WORD COUNT': analysis_results['WORD COUNT'],
                'SYLLABLE PER WORD': analysis_results['SYLLABLE PER WORD'],
                'PERSONAL PRONOUNS': analysis_results['PERSONAL PRONOUNS'],
                'AVG WORD LENGTH': analysis_results['AVG WORD LENGTH']
            }
            
            results.append(result)
            
        except Exception as e:
            print(f"Error processing article {url_id}: {str(e)}")
    
    # Create DataFrame with the specified column order
    output_df = pd.DataFrame(results, columns=[
        'URL_ID', 'URL', 'POSITIVE SCORE', 'NEGATIVE SCORE', 'POLARITY SCORE', 
        'SUBJECTIVITY SCORE', 'AVG SENTENCE LENGTH', 'PERCENTAGE OF COMPLEX WORDS', 
        'FOG INDEX', 'AVG NUMBER OF WORDS PER SENTENCE', 'COMPLEX WORD COUNT', 
        'WORD COUNT', 'SYLLABLE PER WORD', 'PERSONAL PRONOUNS', 'AVG WORD LENGTH'
    ])
    
    output_df.to_excel('Output Data Structure.xlsx', index=False)
    print("Analysis complete. Results saved to 'Output Data Structure.xlsx'")

if __name__ == "__main__":
    main()