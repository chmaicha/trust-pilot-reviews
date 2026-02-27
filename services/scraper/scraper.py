import time
import pandas as pd
import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

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

        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

        service = Service("/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)

        # Anti-detection
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        return driver

    def open_page(self, url):
        self.driver.get(url)

    def accept_cookies(self):
        try:
            wait = WebDriverWait(self.driver, 10)
            accept_button = wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(@aria-label,'Tout accepter')]")
                )
            )
            accept_button.click()
            print("✅ Cookies accepted")
            time.sleep(3)
        except Exception:
            print("No cookie popup detected")

    def open_reviews_panel(self):
        wait = WebDriverWait(self.driver, 30)
        reviews_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@aria-label,'Avis')]")
            )
        )
        reviews_button.click()
        print("✅ Reviews panel opened")
        time.sleep(5)

    def extract_reviews_summary(self):
        wait = WebDriverWait(self.driver, 60)

        reviews_container = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.m6QErb")
            )
        )

        raw_html_reviews = reviews_container.find_elements(
            By.CSS_SELECTOR, "tr.BHOKXe"
        )

        ratings = []
        reviews_counts = []

        for star in raw_html_reviews:
            rating_text = star.get_attribute("aria-label")
            rating_parts = rating_text.split(",")
            stars = rating_parts[0].split()[0]
            num_reviews = rating_parts[1].strip().split()[0].replace(".", "")

            ratings.append(int(stars))
            reviews_counts.append(int(num_reviews))

        print("✅ Summary extracted")

        return pd.DataFrame(
            {"stars": ratings, "reviews": reviews_counts}
        ), reviews_container

    def extract_visible_reviews(self, reviews_container, max_reviews=100):
        reviewers = []
        ratings = []
        review_texts = []
        review_dates = []
        local_guides = []
        text_backups = []
        processed_review_ids = set()

        last_height = self.driver.execute_script(
            "return arguments[0].scrollHeight", reviews_container
        )

        while len(reviewers) < max_reviews:

            raw_html_reviews = self.driver.find_elements(
                By.CSS_SELECTOR, "div.jftiEf.fontBodyMedium"
            )

            for review in raw_html_reviews:

                if len(reviewers) >= max_reviews:
                    break

                try:
                    review_id = review.get_attribute("data-review-id")
                    if review_id in processed_review_ids:
                        continue

                    processed_review_ids.add(review_id)

                    # Expand review
                    try:
                        more_buttons = review.find_elements(
                            By.CSS_SELECTOR, "button.w8nwRe"
                        )
                        for button in more_buttons:
                            if button.is_displayed():
                                button.click()
                                time.sleep(0.3)
                    except:
                        pass

                    reviewer = review.find_element(
                        By.CSS_SELECTOR, "div.d4r55"
                    ).text

                    review_text = review.find_element(
                        By.CSS_SELECTOR, "span.wiI7pd"
                    ).text

                    rating = review.find_element(
                        By.CSS_SELECTOR, "span.kvMYJc"
                    ).get_attribute("aria-label")

                    review_date = review.find_element(
                        By.CSS_SELECTOR, "span.rsqaWe"
                    ).text

                    try:
                        local_guide = review.find_element(
                            By.CLASS_NAME, "RfnDt"
                        ).text
                    except:
                        local_guide = ""

                    reviewers.append(reviewer)
                    review_texts.append(review_text)
                    ratings.append(rating)
                    review_dates.append(review_date)
                    local_guides.append(local_guide)
                    text_backups.append(review.text)

                    print(f"{len(reviewers)}/{max_reviews} collected")

                except Exception:
                    continue

            # Scroll
            self.driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight",
                reviews_container,
            )

            time.sleep(2)

            new_height = self.driver.execute_script(
                "return arguments[0].scrollHeight", reviews_container
            )

            if new_height == last_height:
                print("No more reviews loaded")
                break

            last_height = new_height

        print("🎉 Scraping finished")

        return pd.DataFrame(
            {
                "author": reviewers,
                "local_guide_info": local_guides,
                "rating": ratings,
                "review": review_texts,
                "date_text": review_dates,
                "text_backup": text_backups,
            }
        )

    def close(self):
        self.driver.quit()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Scrape Google Maps reviews"
    )
    parser.add_argument("url", type=str)
    parser.add_argument("csv_name", type=str)

    args = parser.parse_args()

    scraper = GoogleMapsScraper()

    print("Opening page...")
    scraper.open_page(args.url)

    WebDriverWait(scraper.driver, 30).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    time.sleep(5)

    scraper.accept_cookies()
    scraper.open_reviews_panel()

    stars_summary, reviews_container = scraper.extract_reviews_summary()

    collected_reviews = scraper.extract_visible_reviews(
        reviews_container, max_reviews=100
    )



    output_dir = "/app/data/raw"
    os.makedirs(output_dir, exist_ok=True)

    stars_summary.to_csv(
        f"{output_dir}/resumme_{args.csv_name}.csv",
        index=False,
    )

    collected_reviews.to_csv(
        f"{output_dir}/collected_reviews_{args.csv_name}.csv",
        index=False,
    )
    collected_reviews.to_csv(
        f"/app/data/raw/collected_reviews_{args.csv_name}.csv",
        index=False,
    )

    print("✅ Files saved successfully")

    scraper.close()