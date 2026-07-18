import argparse
import logging
import os
import tempfile
import time
from datetime import date

import pandas as pd

from jobs import beautify_excel, excel_file, load_df, load_env_file, required_columns
from jobs_scraper import scrape_all_jobs


SEARCH_TERMS = [
    "backend developer",
    "backend engineer",
    "software engineer",
    "software developer",
    "java developer",
    "java backend developer",
    "python developer",
    "python backend developer",
    "full stack developer",
    "fullstack engineer",
    "spring boot developer",
    "django developer",
    "platform engineer",
    "cloud software engineer",
    "microservices developer",
    "distributed systems engineer",
    "data engineer",
    "fintech software engineer",
]

DEFAULT_SITES = ["linkedin", "indeed", "glassdoor", "zip_recruiter"]
CHECKPOINT_FILE = "batch_scrape_checkpoint.csv"


logging.basicConfig(level=logging.INFO)


def build_job_row(row):
    return {
        "applied": "",
        "AI_recommendation": "",
        "AI_explanation": "",
        "company": row.get("company", ""),
        "title": row.get("title", ""),
        "link": row.get("job_url", row.get("link", "")),
        "description": row.get("description", ""),
        "scrape_date": date.today(),
        "posted_date": row.get("date_posted", row.get("posted_date", "")),
    }


def parse_csv(value):
    return [item.strip() for item in value.split(",") if item.strip()]


def save_results(existing_df, new_rows):
    if not new_rows:
        return

    new_df = pd.DataFrame(new_rows, columns=required_columns)
    out_df = pd.concat([existing_df, new_df], ignore_index=True)
    directory = os.path.dirname(os.path.abspath(excel_file)) or "."
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx", dir=directory) as tmp:
        temp_path = tmp.name
    try:
        out_df.to_excel(temp_path, index=False, engine="openpyxl")
        for attempt in range(10):
            try:
                os.replace(temp_path, excel_file)
                break
            except PermissionError:
                if attempt == 9:
                    raise
                time.sleep(1)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    beautify_excel()
    new_df.to_csv(CHECKPOINT_FILE, index=False)


def scrape_batch(target, terms, sites, location, hours_old, batch_size, max_offsets, distance):
    load_env_file(".env")
    existing_df = load_df()
    unique_urls = set(existing_df["link"].dropna().astype(str))
    new_rows = []

    os.environ["location"] = location
    os.environ["hours_old"] = str(hours_old)
    os.environ["results_wanted"] = str(batch_size)
    os.environ["distance"] = str(distance)
    os.environ.setdefault("country_indeed", "Israel")
    os.environ.setdefault("linkedin_fetch_description", "true")
    os.environ.setdefault("description_format", "markdown")

    for site in sites:
        for term in terms:
            if len(new_rows) >= target:
                save_results(existing_df, new_rows)
                return new_rows

            os.environ["sites"] = site
            os.environ["search_term"] = term

            for offset_index in range(max_offsets):
                if len(new_rows) >= target:
                    break

                offset = offset_index * batch_size
                logging.info(
                    "Scraping site=%s term=%r offset=%s new=%s/%s",
                    site,
                    term,
                    offset,
                    len(new_rows),
                    target,
                )

                try:
                    scraped = scrape_all_jobs(
                        site,
                        term,
                        location,
                        hours_old,
                        batch_size,
                        offset=offset,
                    )
                except Exception:
                    logging.exception("Scrape failed for site=%s term=%r offset=%s", site, term, offset)
                    break

                if scraped is None or scraped.empty:
                    logging.info("No rows returned for site=%s term=%r offset=%s", site, term, offset)
                    break

                before = len(new_rows)
                for _, row in scraped.iterrows():
                    link = str(row.get("job_url", row.get("link", ""))).strip()
                    if not link or link in unique_urls:
                        continue
                    new_rows.append(build_job_row(row))
                    unique_urls.add(link)
                    if len(new_rows) >= target:
                        break

                logging.info("Added %s unique rows from this page", len(new_rows) - before)
                save_results(existing_df, new_rows)

    return new_rows


def parse_args():
    parser = argparse.ArgumentParser(description="Scrape many fresh jobs without AI assessment.")
    parser.add_argument("--target", type=int, default=500)
    parser.add_argument("--location", default="Israel")
    parser.add_argument("--hours-old", type=int, default=168)
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--max-offsets", type=int, default=5)
    parser.add_argument("--distance", type=int, default=50)
    parser.add_argument("--sites", default=",".join(DEFAULT_SITES))
    parser.add_argument("--terms", default=",".join(SEARCH_TERMS))
    return parser.parse_args()


def main():
    args = parse_args()
    rows = scrape_batch(
        target=args.target,
        terms=parse_csv(args.terms),
        sites=parse_csv(args.sites),
        location=args.location,
        hours_old=args.hours_old,
        batch_size=args.batch_size,
        max_offsets=args.max_offsets,
        distance=args.distance,
    )
    logging.info("Finished. New rows scraped: %s", len(rows))


if __name__ == "__main__":
    main()
