import os
import pandas as pd
from src import cleaning


# ==========================================================
# 🚀 FUNCTION TO USE FROM API
# ==========================================================

def run_cleaning(name: str):
    """
    Cleans raw scraped reviews and saves processed file.
    Returns path of cleaned file.
    """

    print(f"🔄 Starting data cleaning for: {name}")

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    raw_data_path = os.path.join(BASE_DIR, "data", "raw")
    processed_path = os.path.join(BASE_DIR, "data", "processed")

    raw_reviews_file = os.path.join(raw_data_path, f"collected_reviews_{name}.csv")
    raw_summary_file = os.path.join(raw_data_path, f"resumme_{name}.csv")

    if not os.path.exists(raw_reviews_file):
        raise FileNotFoundError(f"{raw_reviews_file} not found.")

    reviews_raw = pd.read_csv(raw_reviews_file)
    resumme_raw = pd.read_csv(raw_summary_file)

    reviews = reviews_raw.copy()

    # ===============================
    # 1️⃣ REGEX
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
    # 2️⃣ REMOVE DUPLICATES
    # ===============================

    check_dups = reviews.copy()

    for col in check_dups.columns:
        if check_dups[col].dtype == 'object':
            check_dups[col] = check_dups[col].astype(str)

    duplicates_count = check_dups.duplicated().sum()
    print(f"🗑 Duplicates found: {duplicates_count}")

    reviews.drop_duplicates(inplace=True)

    # ===============================
    # 3️⃣ EXTRACTIONS
    # ===============================

    reviews['local_guide_reviews'] = reviews['local_guide_info'].apply(cleaning.extractReviewCount)
    reviews['rating_score'] = reviews['rating'].apply(cleaning.extractStarRating)

    reviews = cleaning.applyExtractDetails(
        reviews,
        search_words=restaurant_search_words
    )

    reviews['recommendations_list'] = reviews['recommended'].apply(cleaning.extractRecommendations)
    reviews['date'] = reviews['date_text'].apply(cleaning.convertToDate)

    reviews['food_score'] = pd.to_numeric(reviews['food_score'], errors='coerce')
    reviews['service_score'] = pd.to_numeric(reviews['service_score'], errors='coerce')
    reviews['atmosphere_score'] = pd.to_numeric(reviews['atmosphere_score'], errors='coerce')

    reviews['avg_price_per_person'] = reviews['price_per_person'].str.extract(r'-(\d+)\s*€')
    reviews['avg_price_per_person'] = pd.to_numeric(
        reviews['avg_price_per_person'],
        errors='coerce'
    ).astype('Int64')

    reviews.drop(
        columns=[
            'text_backup',
            'local_guide_info',
            'rating',
            'author',
            'recommended',
            'date_text'
        ],
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
    # 4️⃣ HANDLE MISSING VALUES
    # ===============================

    reviews['local_guide_reviews'] = reviews['local_guide_reviews'].fillna(1)
    reviews['rating_score'] = reviews['rating_score'].fillna(1)

    # ===============================
    # 5️⃣ SAVE
    # ===============================

    os.makedirs(processed_path, exist_ok=True)
    output_path = os.path.join(processed_path, f"{name}_reviews.csv")

    reviews.to_csv(output_path, index=False)

    print(f"✅ Cleaning finished. File saved at: {output_path}")

    return {
        "processed_file": output_path,
        "rows_processed": len(reviews)
    }


# ==========================================================
# CLI MODE (Backward compatibility)
# ==========================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str, required=True)

    args = parser.parse_args()

    result = run_cleaning(args.name)

    print(result)