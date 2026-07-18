# AI Job Scraper

Scrape jobs from LinkedIn, Indeed, Glassdoor, and ZipRecruiter into an Excel file, then optionally assess only the new jobs against a personal profile with OpenAI.

The default run scrapes jobs only. AI assessment is a separate step so you can collect jobs cheaply first and decide later when to spend API calls.

## What It Does

- Scrapes jobs with [JobSpy](https://github.com/Bunsly/JobSpy).
- Saves results to `jobs_updated.xlsx`.
- Keeps `AI_recommendation` and `AI_explanation` blank during scraping.
- Deduplicates jobs by link.
- Assesses only rows whose `AI_recommendation` is blank.
- Color-codes Excel recommendations:
  - green: `yes` or `maybe+`
  - yellow: `maybe`
  - red: `no`

## Requirements

- Python 3.10 or newer. Python 3.12 is recommended.
- An OpenAI API key only if you want to run AI assessment.

Install dependencies:

```bash
pip install -r requirements.txt
```

## Setup

1. Create your local environment file:

```bash
copy .env.example .env
```

On macOS/Linux:

```bash
cp .env.example .env
```

2. Edit `.env` with your search settings.

For scraping only, you can leave `api_key` as a placeholder.

For AI assessment, set:

```text
api_key=YOUR_OPENAI_API_KEY
model=gpt-4o-mini
```

3. Create your profile and assessment instructions:

```bash
copy user_profile-example.txt user_profile.txt
copy instructions-example.txt instructions.txt
```

On macOS/Linux:

```bash
cp user_profile-example.txt user_profile.txt
cp instructions-example.txt instructions.txt
```

4. Edit `user_profile.txt` with the candidate resume/profile.

5. Edit `instructions.txt` with the matching rubric. Keep it generic enough that it can evaluate any job row using the profile.

## Basic Usage

Scrape jobs only:

```bash
python jobs.py
```

Assess new, unassessed rows:

```bash
python assess_jobs.py
```

Assess a small batch first:

```bash
python assess_jobs.py --limit 20
```

Count pending rows without calling AI:

```bash
python assess_jobs.py --dry-run
```

Run the old combined flow, scraping and assessing immediately:

```bash
python jobs.py --with-ai
```

## Batch Scraping

Use `batch_scrape_jobs.py` when you want many jobs across multiple search terms:

```bash
python batch_scrape_jobs.py --target 500 --location Israel --hours-old 168
```

Useful options:

```bash
python batch_scrape_jobs.py --target 200 --sites linkedin,indeed --terms "backend developer,java developer,python developer" --batch-size 50
```

The batch scraper writes checkpoints to `batch_scrape_checkpoint.csv` and keeps appending unique jobs to `jobs_updated.xlsx`.

## Configuration

Common `.env` values:

```text
search_term=software engineer
sites=indeed,linkedin,zip_recruiter,glassdoor
results_wanted=25
location=Tel Aviv-Yafo
hours_old=168
country_indeed=Israel
distance=25
linkedin_fetch_description=true
description_format=markdown
```

Optional JobSpy filters:

```text
job_type=fulltime
is_remote=true
easy_apply=true
proxies=host:port,user:pass@host:port
```

Notes:

- `linkedin_fetch_description=true` improves matching because descriptions are richer, but scraping can be slower.
- `country_indeed=Israel` is important for Indeed and Glassdoor searches in Israel.
- Some sites may return fewer results, block scraping, or behave differently over time.

## Output Columns

`jobs_updated.xlsx` contains:

```text
applied
AI_recommendation
AI_explanation
company
title
link
description
scrape_date
posted_date
```

Recommendation meanings:

```text
yes      strong match
maybe+   good match or worth checking
maybe    partial or uncertain match
no       not suitable
```

## Files You Should Not Commit

The repo ignores local/private files such as:

- `.env`
- `instructions.txt`
- `user_profile.txt`
- `jobs_updated.xlsx`
- generated CSV/XLSX files

Use the `*-example.txt` files as templates for sharing.

## Troubleshooting

If `python-jobspy` will not install, check your Python version:

```bash
python --version
```

Use Python 3.10+.

If AI assessment fails, confirm:

- `.env` contains `api_key`
- `instructions.txt` exists
- `user_profile.txt` contains the candidate profile

If scraping returns zero rows, try:

- fewer sites, such as `sites=linkedin`
- a broader `search_term`
- a different `location`
- increasing `hours_old`
