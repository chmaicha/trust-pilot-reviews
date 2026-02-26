import sys
import os
import argparse
import pandas as pd
import numpy as np
import cleaning


def clean_reviews(name: str):

    print(f"🔄 Starting data cleaning for: {name}")

    raw_data_path = 'data/raw/'
    processed_path = 'data/processed/'
    

    reviews_raw = pd.read_csv(f"{raw_data_path}collected_reviews_{name}.csv")
    resumme_raw = pd.read_csv(f"{raw_data_path}resumme_{name}.csv")

    reviews = reviews_raw.copy()

    # ===============================
    # 1️⃣ REGEX ADAPTÉES AU FRANÇAIS
    # ===============================

    restaurant_search_words = {
        'service': r'Service\n([^\n]+)',
        'meal_type': r'Type de repas\n([^\n]+)',
        'price_per_person': r'Prix par personne\n([0-9€\- ]+)',
        'food_score': r'Cuisine\s*:\s*(\d+)',
        'service_score': r'Service\s*:\s*(\d+)',
        'atmosphere_score': r'Ambiance\s*:\s*(\d+)',
        'recommended': r'Plats recommandés\n([^\n]+)'
    }

    # ===============================
    # 2️⃣ SUPPRESSION DES DOUBLONS
    # ===============================

    check_dups = reviews.copy()

    for col in check_dups.columns:
        if check_dups[col].dtype == 'object':
            check_dups[col] = check_dups[col].astype(str)

    duplicates_count = check_dups.duplicated().sum()
    print(f"🗑 Duplicates found: {duplicates_count}")

    reviews.drop_duplicates(inplace=True)

    # ===============================
    # 3️⃣ EXTRACTIONS & TRANSFORMATIONS
    # ===============================

    reviews['local_guide_reviews'] = reviews['local_guide_info'].apply(cleaning.extractReviewCount)
    reviews['rating_score'] = reviews['rating'].apply(cleaning.extractStarRating)

    reviews = cleaning.applyExtractDetails(
        reviews,
        search_words=restaurant_search_words
    )

    reviews['recommendations_list'] = reviews['recommended'].apply(cleaning.extractRecommendations)
    reviews['date'] = reviews['date_text'].apply(cleaning.convertToDate)

    # Conversion numérique
    reviews['food_score'] = pd.to_numeric(reviews['food_score'], errors='coerce')
    reviews['service_score'] = pd.to_numeric(reviews['service_score'], errors='coerce')
    reviews['atmosphere_score'] = pd.to_numeric(reviews['atmosphere_score'], errors='coerce')

    # Extraction prix moyen
    reviews['avg_price_per_person'] = reviews['price_per_person'].str.extract(r'-(\d+)\s*€')
    reviews['avg_price_per_person'] = pd.to_numeric(
        reviews['avg_price_per_person'],
        errors='coerce'
    ).astype('Int64')

    # Drop colonnes inutiles
    reviews.drop(
        columns=['text_backup', 'local_guide_info', 'rating',
                 'author', 'recommended', 'date_text'],
        inplace=True,
        errors='ignore'
    )

    reviews.reset_index(inplace=True)
    reviews.rename(
        columns={
            'index': 'review_id',
            'price_per_person': 'price_per_person_category'
        },
        inplace=True
    )

    # ===============================
    # 4️⃣ GESTION DES VALEURS MANQUANTES
    # ===============================

    reviews['local_guide_reviews'] = reviews['local_guide_reviews'].fillna(1)
    reviews['rating_score'] = reviews['rating_score'].fillna(1)

    # ===============================
    # 5️⃣ SAVE
    # ===============================

    os.makedirs(processed_path, exist_ok=True)
    output_path = f"{processed_path}{name}_reviews.csv"

    reviews.to_csv(output_path, index=False)

    print(f"✅ Cleaning finished. File saved at: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, required=True,
                        help="Restaurant name identifier")
    args = parser.parse_args()

    clean_reviews(args.name)