import pandas as pd
import csv
import re
import logging
from typing import Dict, List, Tuple, Any
from openai import OpenAI
import os
from nltk.tokenize import sent_tokenize
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class NarrativeGenerator:
    def __init__(self):
        """Initialize the NarrativeGenerator with OpenAI client."""
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            logger.warning("OPENAI_API_KEY not found in environment variables")
        else:
            self.client = OpenAI(api_key=self.openai_api_key)

    def load_articles(self, articles_file: str, max_articles: int = None) -> Dict[int, Dict[str, str]]:
        """Load articles from CSV file."""
        articles = {}
        try:
            df = pd.read_csv(articles_file)
            if max_articles:
                df = df.head(max_articles)

            for index, row in df.iterrows():
                article_id = index  # Using index as article ID
                article_title = row.get('Title', f"Article {index+1}")
                article_text = row.get('Full Text of Article', '')

                if article_text:
                    articles[article_id] = {
                        'title': article_title,
                        'text': article_text
                    }

            logger.info(f"Loaded {len(articles)} articles from {articles_file}")
            return articles
        except Exception as e:
            logger.error(f"Error loading articles: {e}")
            return {}

    def summarize_article(self, article_text: str) -> Dict[str, str]:
        """
        Summarize an article according to the specified dimensions.
        """
        try:
            prompt = f"""
            Please analyze the following article and provide a structured summary according to these dimensions:

            1. Blame Attribution:
            - Who is blamed or suspected?
            - Is the attribution direct, indirect, speculative, or disputed?

            2. Victim Entities:
            - Who or what is described as being attacked, damaged, or negatively impacted?
            - Include nations, companies, or infrastructure if applicable.

            3. Geographic Scope:
            - What specific maritime locations, chokepoints, or regions are mentioned?
            - Include countries, straits, cable landing sites, or exclusive economic zones (EEZs).

            4. Plausible Causes:
            - What causes or explanations are provided?
            - List all plausible causes mentioned in the article (e.g., sabotage, anchor drag, espionage, accident).

            5. Economic Consequences:
            - What economic impacts are described or implied?
            - Consider trade disruptions, telecom outages, rerouting costs, insurance, or industry effects.

            6. Environmental Consequences:
            - Are there any environmental harms mentioned?
            - Consider seabed damage, marine life disruption, ecological risk, or pollution.

            Article:
            {article_text}

            Format your response as a JSON object with the six dimensions as keys.
            """

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert analyst who extracts structured information from news articles."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            summary = response.choices[0].message.content
            # Convert the JSON string to a Python dictionary
            import json
            summary_dict = json.loads(summary)

            logger.info("Successfully summarized article")
            return summary_dict

        except Exception as e:
            logger.error(f"Error summarizing article: {e}")
            return {
                "Blame Attribution": "Error in processing",
                "Victim Entities": "Error in processing",
                "Geographic Scope": "Error in processing",
                "Plausible Causes": "Error in processing",
                "Economic Consequences": "Error in processing",
                "Environmental Consequences": "Error in processing"
            }

    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text using OpenAI's embedding API."""
        try:
            response = self.client.embeddings.create(
                input=text,
                model="text-embedding-ada-002"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []

    def cluster_summaries(self, summaries: Dict[int, Dict[str, str]], n_clusters: int = None) -> Dict[int, List[int]]:
        """
        Cluster article summaries based on their embeddings.
        Returns a dictionary mapping cluster IDs to lists of article IDs.
        """
        # Convert summaries to text for embedding
        texts = []
        article_ids = []

        for article_id, summary in summaries.items():
            # Concatenate all summary fields into a single text
            summary_text = " ".join([f"{k}: {v}" for k, v in summary.items()])
            texts.append(summary_text)
            article_ids.append(article_id)

        # Generate embeddings
        embeddings = [self.generate_embedding(text) for text in texts]

        # Determine number of clusters if not specified
        if n_clusters is None:
            n_clusters = min(3, len(texts))  # Default to 3 clusters or fewer if we have fewer articles

        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(embeddings)

        # Group article IDs by cluster
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(article_ids[i])

        return clusters

    def generate_narrative(self, summaries: Dict[int, Dict[str, str]], article_ids: List[int]) -> str:
        """
        Generate a narrative for a cluster of articles based on their summaries.
        """
        try:
            # Collect summaries for the articles in this cluster
            cluster_summaries = {article_id: summaries[article_id] for article_id in article_ids}

            # Format the summaries for the prompt
            formatted_summaries = ""
            for article_id, summary in cluster_summaries.items():
                formatted_summaries += f"Article {article_id}:\n"
                for dimension, content in summary.items():
                    formatted_summaries += f"- {dimension}: {content}\n"
                formatted_summaries += "\n"

            prompt = f"""
            I have a set of article summaries that belong to the same narrative cluster about undersea cable incidents.
            Each summary is structured according to six dimensions: Blame Attribution, Victim Entities, Geographic Scope,
            Plausible Causes, Economic Consequences, and Environmental Consequences.

            Here are the summaries:

            {formatted_summaries}

            Based on these summaries, generate a comprehensive narrative that captures the common themes,
            perspectives, and information across these articles. The narrative should:

            1. Identify the main actors, locations, and events
            2. Highlight consensus and disagreements in blame attribution
            3. Summarize the range of causes suggested
            4. Describe the scope and scale of impacts
            5. Note any unique or outlier perspectives

            Your narrative should be well-structured, approximately 300-500 words, and should accurately
            represent the information contained in the summaries without adding speculation.
            """

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert analyst who synthesizes information from multiple sources into coherent narratives."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )

            narrative = response.choices[0].message.content
            logger.info(f"Generated narrative for cluster with {len(article_ids)} articles")
            return narrative

        except Exception as e:
            logger.error(f"Error generating narrative: {e}")
            return "Error generating narrative."

    def process_articles(self, articles_file: str, max_articles: int = None, n_clusters: int = None) -> Dict[str, Any]:
        """
        Process articles from a CSV file, summarize them, cluster them, and generate narratives.
        """
        try:
            # Load articles
            articles = self.load_articles(articles_file, max_articles)
            if not articles:
                return {"error": "No articles loaded"}

            # Summarize articles
            logger.info(f"Summarizing {len(articles)} articles")
            summaries = {}
            for article_id, article_data in articles.items():
                logger.info(f"Summarizing article {article_id}: {article_data['title']}")
                summary = self.summarize_article(article_data['text'])
                summaries[article_id] = summary

            # Cluster summaries
            logger.info("Clustering article summaries")
            clusters = self.cluster_summaries(summaries, n_clusters)

            # Generate narratives for each cluster
            logger.info(f"Generating narratives for {len(clusters)} clusters")
            narratives = {}
            for cluster_id, article_ids in clusters.items():
                narrative = self.generate_narrative(summaries, article_ids)
                narratives[cluster_id] = {
                    "narrative": narrative,
                    "article_ids": article_ids,
                    "article_count": len(article_ids)
                }

            return {
                "total_articles": len(articles),
                "num_clusters": len(clusters),
                "narratives": narratives,
                "summaries": summaries
            }

        except Exception as e:
            logger.error(f"Error processing articles: {e}")
            return {"error": f"Error processing articles: {str(e)}"}

    def save_narratives_to_csv(self, narratives: Dict[int, Dict], output_file: str = "narratives.csv") -> None:
        """Save the narratives to a CSV file."""
        try:
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'narrative', 'article_count', 'article_ids']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for cluster_id, data in narratives.items():
                    # Replace new lines with pipe character
                    narrative_text = data['narrative']
                    narrative_text = re.sub(r'\n+', '|', narrative_text)

                    writer.writerow({
                        'id': cluster_id,
                        'narrative': narrative_text,
                        'article_count': data['article_count'],
                        'article_ids': ','.join(map(str, data['article_ids']))
                    })

            logger.info(f"Narratives saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving narratives to CSV: {e}")

def main():
    # Use CSV file
    csv_file = "webset-articles_cut_sea_cables.csv"

    generator = NarrativeGenerator()
    results = generator.process_articles(csv_file, max_articles=10, n_clusters=3)

    if "error" in results:
        print(f"Error: {results['error']}")
        return

    print("\n=== Narrative Analysis ===")
    print(f"Total articles: {results['total_articles']}")
    print(f"Number of clusters: {results['num_clusters']}")

    for cluster_id, data in results['narratives'].items():
        print(f"\nCluster {cluster_id} ({data['article_count']} articles):")
        print(f"Article IDs: {data['article_ids']}")
        print(f"Narrative: {data['narrative']}")

    # Save narratives to CSV
    generator.save_narratives_to_csv(results['narratives'])

if __name__ == "__main__":
    main()
