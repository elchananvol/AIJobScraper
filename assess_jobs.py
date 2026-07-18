import argparse
import logging
import os

import pandas as pd

from jobs import beautify_excel, excel_file, load_df, load_env_file, required_columns, split_string


DEFAULT_PROFILE_FILE = "user_profile.txt"
DEFAULT_INSTRUCTIONS_FILE = "instructions.txt"


logging.basicConfig(level=logging.INFO)


def read_text_file(path):
    if not os.path.exists(path):
        return ""
    with open(path, "r", encoding="utf-8") as file:
        return file.read().strip()


def build_assessment_instructions(profile_file, instructions_file):
    instructions = read_text_file(instructions_file)
    profile = read_text_file(profile_file)

    if not profile:
        return instructions

    return (
        f"{instructions}\n\n"
        "Use this candidate profile as the source of truth when assessing jobs:\n"
        f"{profile}"
    )


def is_unassessed(value):
    return pd.isna(value) or str(value).strip() == ""


def create_assistant(profile_file, instructions_file):
    from ai import OpenAIAssistant

    if not os.getenv("api_key"):
        raise ValueError("Missing api_key in .env. Add your OpenAI API key before running AI assessment.")
    if not os.path.exists(instructions_file):
        raise FileNotFoundError(
            f"Missing {instructions_file}. Copy instructions-example.txt to {instructions_file} and edit it."
        )
    instructions = build_assessment_instructions(profile_file, instructions_file)
    assistant = OpenAIAssistant(
        os.getenv("api_key"),
        "MyJobsMatcher",
        instructions,
        os.getenv("model"),
        os.getenv("assistant_id"),
    )
    logging.info("Assistant created successfully. assistant ID: %s", assistant.assistant_id)
    return assistant


def assess_new_jobs(profile_file, instructions_file, limit=None, dry_run=False):
    load_env_file(".env")
    df = load_df()

    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    rows_to_assess = df[df["AI_recommendation"].apply(is_unassessed)]
    if limit is not None:
        rows_to_assess = rows_to_assess.head(limit)

    logging.info("Rows pending assessment: %s", len(rows_to_assess))
    if rows_to_assess.empty or dry_run:
        return len(rows_to_assess)

    assistant = create_assistant(profile_file, instructions_file)
    for index, row in rows_to_assess.iterrows():
        msg = (
            f"title: {row.get('title', '')}. "
            f"company: {row.get('company', '')}. "
            f"description: {row.get('description', '')}"
        )
        ai_response = assistant.submit_message(msg)
        recommendation, explanation = split_string(ai_response)
        df.at[index, "AI_recommendation"] = recommendation
        df.at[index, "AI_explanation"] = explanation
        logging.info("Assessed row %s: %s", index, recommendation)

    df.to_excel(excel_file, index=False, engine="openpyxl")
    beautify_excel()
    return len(rows_to_assess)


def parse_args():
    parser = argparse.ArgumentParser(description="Assess only new, unassessed jobs in the Excel table.")
    parser.add_argument("--profile-file", default=DEFAULT_PROFILE_FILE)
    parser.add_argument("--instructions-file", default=DEFAULT_INSTRUCTIONS_FILE)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Count pending rows without calling AI.")
    return parser.parse_args()


def main():
    args = parse_args()
    assessed_count = assess_new_jobs(
        profile_file=args.profile_file,
        instructions_file=args.instructions_file,
        limit=args.limit,
        dry_run=args.dry_run,
    )
    logging.info("Assessment complete. Rows processed or pending in dry-run: %s", assessed_count)


if __name__ == "__main__":
    main()
