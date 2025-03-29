#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import re
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
import nltk
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Tuple
import logging
import csv
import pandas as pd

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Download NLTK resources if not already downloaded
try:
    nltk.data.find('punkt_tab')
except:
    nltk.download('punkt_tab')

from nltk.tokenize import sent_tokenize, word_tokenize

class NewsArticleProcessor:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        else:
            self.client = OpenAI(api_key=self.openai_api_key)

    def extract_article_content(self, url: str) -> str:
        """Extract the main content from a news article URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()

            # Look for article content in common containers
            article_content = None

            # Try different selectors commonly used for article content
            selectors = [
                'article',
                '.article-content',
                '.story-content',
                '.post-content',
                'main',
                '#content',
                '.content'
            ]

            for selector in selectors:
                content = soup.select(selector)
                if content:
                    article_content = content[0]
                    break

            # If no specific container found, use the body
            if not article_content:
                article_content = soup.body

            # Extract text and clean it
            if article_content:
                text = article_content.get_text(separator=' ', strip=True)
                # Clean up whitespace
                text = re.sub(r'\s+', ' ', text)
                return text

            return ""
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return ""

    def split_into_units(self, text: str) -> List[str]:
        """Split the article content into meaningful units (paragraphs or sentences)."""
        # First split by paragraphs
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        # Merge short paragraphs (less than 20 words) with the next paragraph
        merged_paragraphs = []
        i = 0
        while i < len(paragraphs):
            current_paragraph = paragraphs[i]
            word_count = len(current_paragraph.split())
            
            # If current paragraph is too short and not the last one
            if word_count < 20 and i < len(paragraphs) - 1:
                # Merge with the next paragraph
                merged_text = current_paragraph + " " + paragraphs[i + 1]
                # Skip the next paragraph since we've merged it
                i += 2
                merged_paragraphs.append(merged_text)
            else:
                # Keep the paragraph as is
                merged_paragraphs.append(current_paragraph)
                i += 1
                
        # Replace original paragraphs with merged ones
        paragraphs = merged_paragraphs

        # If paragraphs are too long, split them into sentences
        units = []
        for paragraph in paragraphs:
            if len(paragraph.split()) > 200:  # If paragraph has more than 200 words
                sentences = sent_tokenize(paragraph)
                units.extend(sentences)
            else:
                units.append(paragraph)

        return units

    def generate_embeddings(self, units: List[str]) -> np.ndarray:
        """Generate embeddings for each text unit."""
        return self.model.encode(units)

    def identify_clusters(self, embeddings: np.ndarray, min_clusters: int = 2, max_clusters: int = 10) -> Tuple[List[int], int]:
        """Identify optimal number of clusters and assign cluster labels."""
        if len(embeddings) < min_clusters:
            return [0] * len(embeddings), 1

        # Find optimal number of clusters using silhouette score
        best_score = -1
        best_n_clusters = min_clusters
        best_labels = None

        for n_clusters in range(min_clusters, min(max_clusters + 1, len(embeddings))):
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(embeddings)

            # Skip if any cluster has only one sample (can't compute silhouette)
            cluster_sizes = np.bincount(labels)
            if min(cluster_sizes) < 2:
                continue

            score = silhouette_score(embeddings, labels)

            if score > best_score:
                best_score = score
                best_n_clusters = n_clusters
                best_labels = labels

        # If we couldn't find a good clustering, default to min_clusters
        if best_labels is None:
            kmeans = KMeans(n_clusters=min_clusters, random_state=42, n_init=10)
            best_labels = kmeans.fit_predict(embeddings)
            best_n_clusters = min_clusters

        return best_labels.tolist(), best_n_clusters

    def generate_narrative(self, units: List[str], cluster_id: int) -> str:
        """Generate a narrative summary for a cluster using LLM."""
        if not self.openai_api_key:
            return "OpenAI API key not provided. Cannot generate narrative."

        try:
            combined_text = "\n\n".join(units)
            # Check if the combined text is too long and truncate if necessary
            word_count = len(combined_text.split())
            if word_count > 50000:
                logger.info(f"Truncating combined text from {word_count} to 50000 words for cluster {cluster_id}")
                words = combined_text.split()
                combined_text = " ".join(words[:50000])

            response = self.client.chat.completions.create(model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that identifies the main narrative or theme from a collection of news article excerpts."},
                {"role": "user", "content": f"Based on these paragraphs, identify a narrative with these details (a) actor(s) blamed for the cause of the cable cutting event, b) actor(s) credited for saving the cable cutting event, c) the location at which the cable cutting happened, d) what the speculated cause of the cable cutting was, malicious? accidental? coordinated?\n\n{combined_text}"}
            ],
            max_tokens=150,
            temperature=0.5)

            narrative = response.choices[0].message.content.strip()
            return narrative
        except Exception as e:
            logger.error(f"Error generating narrative for cluster {cluster_id}: {e}")
            return f"Error generating narrative: {str(e)}"

    def process_articles_from_csv(self, csv_file: str, max_articles: int = 10) -> Dict[str, Any]:
        """Process articles from a CSV file and identify sub-narratives."""
        all_units = []
        article_to_units_map = {}

        try:
            # Read the CSV file
            df = pd.read_csv(csv_file)
            
            # Limit to first max_articles
            df = df.head(max_articles)
            
            # Extract full text from each article
            for index, row in df.iterrows():
                article_title = row.get('Title', f"Article {index+1}")
                article_text = row.get('Full Text of Article', '')
                
                logger.info(f"Processing article: {article_title}")
                
                if article_text:
                    # Split content into units
                    units = self.split_into_units(article_text)
                    article_to_units_map[article_title] = units
                    all_units.extend(units)
                else:
                    logger.warning(f"No content found for article: {article_title}")
            
            if not all_units:
                return {"error": "No valid content extracted from any of the articles in the CSV"}
                
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(all_units)} text units")
            embeddings = self.generate_embeddings(all_units)
            
            # Identify clusters
            logger.info("Identifying clusters")
            cluster_labels, num_clusters = self.identify_clusters(embeddings)
            
            # Group units by cluster
            clusters = {}
            for i, label in enumerate(cluster_labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(all_units[i])
            
            # Generate narrative for each cluster
            logger.info(f"Generating narratives for {num_clusters} clusters")
            narratives = {}
            for cluster_id, units in clusters.items():
                narrative = self.generate_narrative(units, cluster_id)
                narratives[cluster_id] = {
                    "narrative": narrative,
                    "sample_units": units[:5],  # Include a few sample units
                    "unit_count": len(units)
                }
            
            return {
                "total_units": len(all_units),
                "num_clusters": num_clusters,
                "narratives": narratives
            }
            
        except Exception as e:
            logger.error(f"Error processing CSV file: {e}")
            return {"error": f"Error processing CSV file: {str(e)}"}

    def save_narratives_to_csv(self, narratives: Dict[int, Dict], output_file: str = "narratives.csv") -> None:
        """Save the narratives to a CSV file."""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'narrative']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for cluster_id, data in narratives.items():
                    # Replace new lines with pipe character
                    narrative_text = data['narrative']
                    narrative_text = re.sub(r'\n+', '|', narrative_text)
                    
                    writer.writerow({
                        'id': cluster_id,
                        'narrative': narrative_text
                    })
                
            logger.info(f"Narratives saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving narratives to CSV: {e}")

def main():
    # Use CSV file instead of URLs
    csv_file = "webset-articles_cut_sea_cables.csv"
    
    processor = NewsArticleProcessor()
    results = processor.process_articles_from_csv(csv_file, max_articles=20)
    
    if "error" in results:
        print(f"Error: {results['error']}")
        return

    print("\n=== Sub-Narratives Analysis ===")
    print(f"Total text units: {results['total_units']}")
    print(f"Number of clusters: {results['num_clusters']}")

    for cluster_id, data in results['narratives'].items():
        print(f"\nCluster {cluster_id} ({data['unit_count']} units):")
        print(f"Narrative: {data['narrative']}")
        print("Sample text units:")
        for i, unit in enumerate(data['sample_units'], 1):
            print(f"  {i}. {unit[:100]}...")
    
    # Save narratives to CSV
    processor.save_narratives_to_csv(results['narratives'])

if __name__ == "__main__":
    main()
