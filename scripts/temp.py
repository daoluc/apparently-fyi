# Example of using NLTK (Natural Language Toolkit)

# Import necessary libraries
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer
import string

# Download required NLTK resources (uncomment if needed)
try:
    nltk.data.find('punkt_tab')
except:
    nltk.download('punkt_tab')
try:
    nltk.data.find('stopwords')
except:
    nltk.download('stopwords')
try:
    nltk.data.find('wordnet')
except:
    nltk.download('wordnet')
try:
    nltk.data.find('averaged_perceptron_tagger_eng')
except:
    nltk.download('averaged_perceptron_tagger_eng')

# Sample text for processing
sample_text = """Natural Language Processing (NLP) is a field of artificial intelligence 
that focuses on the interaction between computers and humans through natural language. 
The ultimate objective of NLP is to read, decipher, understand, and make sense of human language 
in a valuable way."""

# 1. Sentence Tokenization
print("Sentence Tokenization:")
sentences = sent_tokenize(sample_text)
for i, sentence in enumerate(sentences):
    print(f"Sentence {i+1}: {sentence}")

# 2. Word Tokenization
print("\nWord Tokenization:")
words = word_tokenize(sample_text)
print(words[:10])  # Print first 10 words

# 3. Removing Stopwords
print("\nRemoving Stopwords:")
stop_words = set(stopwords.words('english'))
filtered_words = [word for word in words if word.lower() not in stop_words]
print(filtered_words[:10])  # Print first 10 filtered words

# 4. Stemming (reducing words to their root form)
print("\nStemming:")
stemmer = PorterStemmer()
stemmed_words = [stemmer.stem(word) for word in filtered_words]
print(stemmed_words[:10])  # Print first 10 stemmed words

# 5. Lemmatization (reducing words to their base form)
print("\nLemmatization:")
lemmatizer = WordNetLemmatizer()
lemmatized_words = [lemmatizer.lemmatize(word) for word in filtered_words]
print(lemmatized_words[:10])  # Print first 10 lemmatized words

# 6. Part-of-Speech Tagging
print("\nPart-of-Speech Tagging:")
nltk.download('averaged_perceptron_tagger', quiet=True)
pos_tags = nltk.pos_tag(words[:10])
print(pos_tags)

# 7. Named Entity Recognition
print("\nNamed Entity Recognition:")
nltk.download('maxent_ne_chunker', quiet=True)
nltk.download('words', quiet=True)
ner_tree = nltk.ne_chunk(nltk.pos_tag(word_tokenize("Google was founded by Larry Page and Sergey Brin.")))
print(ner_tree)
