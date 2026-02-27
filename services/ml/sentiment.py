import pandas as pd
import numpy as np
import sys
import os
import json
from tqdm import tqdm

import ml_processing
import plots


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
processed_data_path = os.path.join(BASE_DIR, 'data', 'processed') + os.sep
raw_data_path = os.path.join(BASE_DIR, 'data', 'raw') + os.sep

sys.path.append(os.path.abspath(os.path.join('..')))

label_mapping = {
    'rating_score': 'Rating',
    'food_score': 'Food',
    'service_score': 'Service',
    'atmosphere_score': 'Ambient'
}

number_of_words = 10
n_grams = 2
eps = 0.5
min_samples = 10


# ==========================================================
# 🚀 MAIN FUNCTION (API READY)
# ==========================================================

def run_sentiment(name: str, plot: bool = True):

    reviews_pro = pd.read_csv(processed_data_path + name + '_reviews.csv')
    resumme_raw = pd.read_csv(raw_data_path + 'resumme_' + name + '.csv')

    print(resumme_raw)
    print(reviews_pro.sample(5))

    reviews = reviews_pro.copy()
    reviews.reset_index(drop=True, inplace=True)
    resumme = resumme_raw.copy()

    # ===============================
    # Cleaning
    # ===============================
    tqdm.pandas(desc="Cleaning Reviews")
    reviews['cleaned_review'] = reviews['review'].fillna('').progress_apply(
        ml_processing.clean_text
    )

    print(reviews[['review', 'cleaned_review']].sample(5))

    label_keys = list(label_mapping.keys())

    # ===============================
    # Sentiment
    # ===============================
    reviews = ml_processing.analyzeSentiment(reviews)

    common_positive_words = ml_processing.extractCommonWords(
        reviews, sentiment_label='positive', n=number_of_words
    )
    common_negative_words = ml_processing.extractCommonWords(
        reviews, sentiment_label='negative', n=number_of_words
    )

    common_positive_bigrams = ml_processing.extractCommonNgrams(
        reviews, sentiment_label='positive', n=n_grams, top_n=number_of_words
    )
    common_negative_bigrams = ml_processing.extractCommonNgrams(
        reviews, sentiment_label='negative', n=n_grams, top_n=number_of_words
    )

    if plot:
        plots.plotSentimentTrend(reviews, years_limit=2)

    # ===============================
    # Embeddings
    # ===============================
    tqdm.pandas(desc="Generating Embeddings")
    reviews['embedding'] = reviews['cleaned_review'].progress_apply(
        ml_processing.get_embedding
    )

    embeddings_pca = ml_processing.calculateAndVisualizeEmbeddingsPCA(
        reviews, score_column=label_keys[0], plot=plot
    )

    embeddings_umap = ml_processing.calculateAndVisualizeEmbeddingsUMAP(
        reviews, plot
    )

    pca_clusters = ml_processing.calculateAndVisualizeEmbeddingsPCA_with_DBSCAN(
        reviews, score_column=label_keys[0], eps=eps,
        min_samples=min_samples, plot=plot
    )

    umap_clusters = ml_processing.calculateAndVisualizeEmbeddingsUMAP_with_DBSCAN(
        reviews, eps=eps, min_samples=min_samples, plot=plot
    )

    reviews.reset_index(drop=True, inplace=True)
    reviews['review_id'] = reviews.index

    reviews = (
        reviews
        .drop(columns=['pca_cluster', 'umap_cluster'], errors='ignore')
        .merge(pca_clusters[['review_id', 'pca_cluster']], on='review_id', how='left')
        .merge(umap_clusters[['review_id', 'umap_cluster']], on='review_id', how='left')
    )

    # ===============================
    # Save ML file
    # ===============================
    ml_file_path = processed_data_path + name + '_ml_processed_reviews.csv'
    reviews.to_csv(ml_file_path, index=False)

    # ===============================
    # Topics
    # ===============================
    lda_model, topics = ml_processing.analyzeTopicsLDA(reviews)

    group_columns = ['pca_cluster', 'umap_cluster', 'sentiment_label']
    topics_dict = ml_processing.generateTopicsbyColumn(reviews, group_columns)

    time_period = 'month'
    num_periods = 3

    negative_periods_rating_reviews, low_score_periods = ml_processing.analyzeLowScores(
        reviews, label_keys[0], time_period, num_periods
    )

    negative_periods_food_reviews, _ = ml_processing.analyzeLowScores(
        reviews, label_keys[1], time_period, num_periods
    )

    negative_periods_service_reviews, _ = ml_processing.analyzeLowScores(
        reviews, label_keys[2], time_period, num_periods
    )

    negative_periods_atmosphere_reviews, _ = ml_processing.analyzeLowScores(
        reviews, label_keys[3], time_period, num_periods
    )

    negative_periods_rating_topics = ml_processing.generateTopicsPerPeriod(
        negative_periods_rating_reviews, label_keys[0]
    )

    negative_periods_food_topics = ml_processing.generateTopicsPerPeriod(
        negative_periods_food_reviews, label_keys[1]
    )

    negative_periods_service_topics = ml_processing.generateTopicsPerPeriod(
        negative_periods_service_reviews, label_keys[2]
    )

    negative_periods_atmosphere_topics = ml_processing.generateTopicsPerPeriod(
        negative_periods_atmosphere_reviews, label_keys[3]
    )

    negative_periods_topics = {
        **negative_periods_rating_topics,
        **negative_periods_food_topics,
        **negative_periods_service_topics,
        **negative_periods_atmosphere_topics
    }

    # ===============================
    # Words dictionary
    # ===============================
    words_dict = {
        "common_positive_words": ml_processing.format_words(common_positive_words),
        "common_negative_words": ml_processing.format_words(common_negative_words),
        "common_positive_bigrams": ml_processing.format_words(common_positive_bigrams),
        "common_negative_bigrams": ml_processing.format_words(common_negative_bigrams)
    }

    reviews_summary_dict = {**topics_dict, **words_dict}

    # ===============================
    # Samples selection
    # ===============================
    reviews_score = reviews.copy()

    food_score_mean = np.round(reviews_score[label_keys[1]].mean(), 2) / 5
    service_score_mean = np.round(reviews_score[label_keys[2]].mean(), 2) / 5
    atmosphere_score_mean = np.round(reviews_score[label_keys[3]].mean(), 2) / 5

    reviews_score[label_keys[1]] = reviews_score[label_keys[1]].fillna(food_score_mean)
    reviews_score[label_keys[2]] = reviews_score[label_keys[2]].fillna(service_score_mean)
    reviews_score[label_keys[3]] = reviews_score[label_keys[3]].fillna(atmosphere_score_mean)

    reviews_score['total_score'] = np.round(
        reviews_score[label_keys[0]] +
        (reviews_score[label_keys[1]]/5 +
         reviews_score[label_keys[2]]/5 +
         reviews_score[label_keys[3]]/5) / 3, 2)

    valid_reviews = reviews_score[reviews_score['review'].notna()]

    best_reviews = valid_reviews[valid_reviews['total_score'] > 5]
    worst_reviews = valid_reviews[valid_reviews['total_score'] < 2.5]

    recent_best_reviews = best_reviews.sort_values(by='date', ascending=False)
    recent_worst_reviews = worst_reviews.sort_values(by='date', ascending=False)

    best_reviews_sample = best_reviews.sort_values(by='total_score', ascending=False)
    worst_reviews_sample = worst_reviews.sort_values(by='total_score', ascending=True)

    low_score_reviews = negative_periods_rating_reviews[
        negative_periods_rating_reviews['review'].notna()
    ][['month','review',label_keys[0]]]

    recent_best_reviews['sample_type'] = 'recent_best_reviews'
    recent_worst_reviews['sample_type'] = 'recent_worst_reviews'
    best_reviews_sample['sample_type'] = 'best_reviews_sample'
    worst_reviews_sample['sample_type'] = 'worst_reviews_sample'
    low_score_reviews['sample_type'] = 'low_score_reviews'

    combined_reviews = pd.concat([
        recent_best_reviews,
        recent_worst_reviews,
        best_reviews_sample,
        worst_reviews_sample,
        low_score_reviews
    ])

    sample_file_path = processed_data_path + name + '_sample_selected_reviews.csv'
    combined_reviews.reset_index(drop=True, inplace=True)
    combined_reviews.to_csv(sample_file_path, index=False)

    # ===============================
    # LLM Insights
    # ===============================
    client = llm_insights.initChatGPTClient()

    general_prompt = "... SAME PROMPT AS YOUR ORIGINAL ..."
    general_insights = llm_insights.extractInsightsWithLLM(
        reviews_summary_dict, general_prompt, client
    )

    general_json_path = processed_data_path + name + '_general_insights.json'
    with open(general_json_path, 'w') as f:
        json.dump(general_insights, f, indent=4)

    worst_prompt = "... SAME PROMPT AS YOUR ORIGINAL ..."
    worst_insights = llm_insights.extractInsightsWithLLM(
        negative_periods_topics, worst_prompt, client
    )

    worst_json_path = processed_data_path + name + '_worst_periods_insights.json'
    with open(worst_json_path, 'w') as f:
        json.dump(worst_insights, f, indent=4)

    return {
        "ml_file": ml_file_path,
        "samples_file": sample_file_path,
        "reviews_processed": len(reviews)
    }


# ==========================================================
# CLI MODE
# ==========================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Process sentiment analysis.')
    parser.add_argument('--name', type=str, required=True)
    parser.add_argument('--plot', type=bool, default=True)

    args = parser.parse_args()

    result = run_sentiment(args.name, args.plot)

    print("✅ Sentiment pipeline completed.")
    print(result)