import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def combine_data():
    """
    Combine narrative_article_mapping.csv with articles2.csv and create a new CSV file
    with selected columns: narrative_id, article_id, agreement_score, Title, Media Location, Published Date
    """
    try:
        # Load the mapping data
        logger.info("Loading narrative_article_mapping.csv")
        mapping_df = pd.read_csv("narrative_article_mapping.csv")
        
        # Load the articles data
        logger.info("Loading articles2.csv")
        articles_df = pd.read_csv("articles2.csv")
        
        # Check if 'article_id' already exists in articles_df
        if 'article_id' in articles_df.columns:
            # Rename the existing article_id column to avoid duplication
            articles_df = articles_df.rename(columns={"article_id": "original_article_id"})
        
        # Reset index in articles_df to match article_id in mapping_df
        articles_df = articles_df.reset_index().rename(columns={"index": "article_id"})
        
        # Process Media Location to get only the last part after the last comma
        articles_df['Media Location'] = articles_df['Media Location'].apply(
            lambda x: x.split(',')[-1].strip().rstrip('.') if isinstance(x, str) else x
        )
        
        # Merge the dataframes on article_id
        logger.info("Merging dataframes")
        combined_df = pd.merge(
            mapping_df,
            articles_df[["article_id", "Title", "Media Location", "Published Date"]],
            on="article_id",
            how="left"
        )
        
        # Select only the required columns
        result_df = combined_df[["narrative_id", "article_id", "agreement_score", "Title", "Media Location", "Published Date"]]
        
        # Save the combined data to a new CSV file
        output_file = "combined_narrative_articles.csv"
        logger.info(f"Saving combined data to {output_file}")
        result_df.to_csv(output_file, index=False)
        
        logger.info(f"Successfully combined data and saved to {output_file}")
        print(f"Combined data saved to {output_file}")
        
        return result_df
    
    except Exception as e:
        logger.error(f"Error combining data: {e}")
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    combine_data()
