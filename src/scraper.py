import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class GoogleMapsScraper:
    def __init__(self):
        self.driver = self._init_driver()

      
    def _init_driver(self):
        chrome_options = Options()
        chrome_options.binary_location = "/usr/bin/chromium"

        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        return webdriver.Chrome(options=chrome_options)



    def open_page(self, url):
        self.driver.get(url)
        time.sleep(5)

    def accept_cookies(self):
        try:
            accept_button = self.driver.find_element(
                By.XPATH, "//button[@aria-label='Tout accepter']"
            )
            accept_button.click()
            time.sleep(3)
        except Exception:
            pass

    def extract_reviews_summary(self):
        wait = WebDriverWait(self.driver, 30)
        reviews_container = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'div.m6QErb.DxyBCb.kA9KIf.dS8AEf.XiKgde')
            )
        )

        raw_html_reviews = reviews_container.find_elements(
            By.CSS_SELECTOR, 'tr.BHOKXe'
        )

        ratings = []
        reviews_counts = []

        for star in raw_html_reviews:
            rating_text = star.get_attribute('aria-label')
            rating_parts = rating_text.split(',')
            stars = rating_parts[0].split()[0]
            num_reviews = rating_parts[1].strip().split()[0].replace('.', '')

            ratings.append(int(stars))
            reviews_counts.append(int(num_reviews))

        return pd.DataFrame({'stars': ratings, 'reviews': reviews_counts}), reviews_container

    def extract_visible_reviews(self, reviews_container, max_reviews=100):

        reviewers, ratings, review_texts = [], [], []
        review_dates, local_guides, text_backups = [], [], []
        processed_review_ids = set()

        last_height = self.driver.execute_script(
            "return arguments[0].scrollHeight", reviews_container
        )

        while len(reviewers) < max_reviews:

            raw_html_reviews = self.driver.find_elements(
                By.CSS_SELECTOR, 'div.jftiEf.fontBodyMedium'
            )

            for review in raw_html_reviews:

                if len(reviewers) >= max_reviews:
                    break

                try:
                    review_id = review.get_attribute('data-review-id')
                    if review_id in processed_review_ids:
                        continue

                    processed_review_ids.add(review_id)

                    reviewer = review.find_element(By.CSS_SELECTOR, 'div.d4r55').text
                    review_text = review.find_element(By.CSS_SELECTOR, 'span.wiI7pd').text
                    rating = review.find_element(By.CSS_SELECTOR, 'span.kvMYJc').get_attribute('aria-label')
                    review_date = review.find_element(By.CSS_SELECTOR, 'span.rsqaWe').text

                    try:
                        local_guide = review.find_element(By.CLASS_NAME, "RfnDt").text
                    except:
                        local_guide = ''

                    reviewers.append(reviewer)
                    review_texts.append(review_text)
                    ratings.append(rating)
                    review_dates.append(review_date)
                    local_guides.append(local_guide)
                    text_backups.append(review.text)

                except:
                    continue

            self.driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight",
                reviews_container
            )

            time.sleep(2)

            new_height = self.driver.execute_script(
                "return arguments[0].scrollHeight",
                reviews_container
            )

            if new_height == last_height:
                break

            last_height = new_height

        return pd.DataFrame({
            'author': reviewers,
            'local_guide_info': local_guides,
            'rating': ratings,
            'review': review_texts,
            'date_text': review_dates,
            'text_backup': text_backups
        })

    def close(self):
        self.driver.quit()


# ==========================================================
# 🚀 FUNCTION USED BY MICROSERVICE
# ==========================================================

def run_scraper(url: str, name: str, max_reviews: int = 100):

    scraper = GoogleMapsScraper()
    scraper.open_page(url)
    scraper.accept_cookies()

    stars_summary, reviews_container = scraper.extract_reviews_summary()
    collected_reviews = scraper.extract_visible_reviews(
        reviews_container,
        max_reviews=max_reviews
    )

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    raw_data_path = os.path.join(BASE_DIR, 'data', 'raw')
    os.makedirs(raw_data_path, exist_ok=True)

    summary_path = os.path.join(raw_data_path, f'resumme_{name}.csv')
    reviews_path = os.path.join(raw_data_path, f'collected_reviews_{name}.csv')

    stars_summary.to_csv(summary_path, index=False)
    collected_reviews.to_csv(reviews_path, index=False)

    scraper.close()

    return {
        "summary_file": summary_path,
        "reviews_file": reviews_path,
        "reviews_collected": len(collected_reviews)
    }


# ==========================================================
# CLI MODE (BACKWARD COMPATIBLE)
# ==========================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("csv_name")
    parser.add_argument("--max_reviews", type=int, default=100)

    args = parser.parse_args()

    result = run_scraper(args.url, args.csv_name, args.max_reviews)
    print(result)