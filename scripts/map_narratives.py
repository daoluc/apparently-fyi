import pandas as pd
import csv
import re
import logging
from typing import Dict, List, Tuple
from openai import OpenAI
import os
from nltk.tokenize import sent_tokenize
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NarrativeMapper:
    def __init__(self):
        """Initialize the NarrativeMapper with OpenAI client."""
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        else:
            self.client = OpenAI(api_key=self.openai_api_key)
    
    def load_narratives(self, narratives_file: str) -> Dict[int, str]:
        """Load narratives from CSV file."""
        narratives = {}
        try:
            df = pd.read_csv(narratives_file)
            for _, row in df.iterrows():
                narratives[row['id']] = row['narrative']
            logger.info(f"Loaded {len(narratives)} narratives from {narratives_file}")
            return narratives
        except Exception as e:
            logger.error(f"Error loading narratives: {e}")
            return {}
    
    def load_articles(self, articles_file: str) -> Dict[int, str]:
        """Load articles from CSV file."""
        articles = {}
        try:
            df = pd.read_csv(articles_file)
            # Only load top 10 articles
            df = df.head(10)
            for index, row in df.iterrows():
                article_id = index  # Using index as article ID
                article_text = row.get('Full Text of Article', '')
                if article_text:
                    articles[article_id] = article_text
            logger.info(f"Loaded {len(articles)} articles from {articles_file}")
            return articles
        except Exception as e:
            logger.error(f"Error loading articles: {e}")
            return {}
    
    def evaluate_agreement(self, article_text: str, narrative: str) -> float:
        """
        Evaluate the agreement between article and narrative.
        Returns a score between -1 (complete disagreement) and 1 (complete agreement).
        """
        if not self.openai_api_key:
            logger.warning("OpenAI API key not provided. Cannot evaluate agreement.")
            return 0.0
        
        try:
            # Truncate article text if too long
            if len(article_text) > 15000:
                article_text = article_text[:15000] + "..."
            
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an objective analyst evaluating how news articles align with specific narratives."},
                    {"role": "user", "content": f"""
                    Evaluate how much this article agrees or disagrees with the given narrative.
                    
                    NARRATIVE: {narrative}
                    
                    ARTICLE: {article_text}
                    
                    Assign a score from -1 to 1 where:
                    - Scores from 0 to 1 indicate agreement (1 being complete agreement)
                    - Scores from 0 to -1 indicate disagreement (-1 being complete disagreement)
                    - 0 indicates neutrality or no relation
                    
                    Return only the numerical score without any explanation.
                    """}
                ],
                max_tokens=10,
                temperature=0.2
            )
            
            score_text = response.choices[0].message.content.strip()
            # Extract the numerical value
            try:
                score = float(re.search(r'-?\d+\.?\d*', score_text).group())
                # Ensure the score is within the range [-1, 1]
                score = max(-1.0, min(1.0, score))
                return score
            except (ValueError, AttributeError):
                logger.warning(f"Could not parse score from response: {score_text}")
                return 0.0
                
        except Exception as e:
            logger.error(f"Error evaluating agreement: {e}")
            return 0.0
    
    def map_narratives_to_articles(self, narratives: Dict[int, str], articles: Dict[int, str]) -> List[Tuple[int, int, float]]:
        """Map narratives to articles and evaluate agreement."""
        results = []
        total_evaluations = len(narratives) * len(articles)
        completed = 0
        
        for narrative_id, narrative_text in narratives.items():
            for article_id, article_text in articles.items():
                logger.info(f"Evaluating narrative {narrative_id} against article {article_id} ({completed+1}/{total_evaluations})")
                score = self.evaluate_agreement(article_text, narrative_text)
                results.append((narrative_id, article_id, score))
                completed += 1
                
        return results
    
    def save_results(self, results: List[Tuple[int, int, float]], output_file: str = "narrative_article_mapping.csv") -> None:
        """Save the mapping results to a CSV file."""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['narrative_id', 'article_id', 'agreement_score']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for narrative_id, article_id, score in results:
                    writer.writerow({
                        'narrative_id': narrative_id,
                        'article_id': article_id,
                        'agreement_score': score
                    })
                
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving results to CSV: {e}")

def main():
    articles_file = "webset-articles_cut_sea_cables.csv"
    narratives_file = "narratives.csv"
    output_file = "narrative_article_mapping.csv"
    
    mapper = NarrativeMapper()
    
    # Load narratives and articles
    narratives = mapper.load_narratives(narratives_file)
    articles = mapper.load_articles(articles_file)
    
    if not narratives or not articles:
        logger.error("Failed to load narratives or articles. Exiting.")
        return
    
    # Map narratives to articles
    results = mapper.map_narratives_to_articles(narratives, articles)
    
    # Save results
    mapper.save_results(results, output_file)
    
    print(f"Completed mapping {len(narratives)} narratives to {len(articles)} articles.")
    print(f"Results saved to {output_file}")

if __name__ == "__main__":
    main()
