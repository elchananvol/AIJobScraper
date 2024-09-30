from link_scraper import *
from ai import *
from jobs_scraper import *
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import os

excel_file = "jobs.xlsx"
required_columns = ["applied", "AI_recommendation", "AI_explanation", "company", "title", "link", "description",
                    "scrape_date",
                    "posted_date"]
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', None)


def load_env_file(file_path):
    with open(file_path) as f:
        for line in f:
            # Ignore comments and empty lines
            if line.strip() and not line.startswith('#') and not line.startswith(';'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value


def load_df():
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file, engine='openpyxl')
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")
    else:
        df = pd.DataFrame(columns=required_columns)
    return df


def split_string(input_string):
    starting_words = ["yes", "no", "maybe+", "maybe"]
    for word in starting_words:
        if input_string.startswith(word):
            return word, input_string[len(word):].strip()


def beautify_excel():
    wb = load_workbook(excel_file)
    ws = wb.active
    ws.auto_filter.ref = ws.dimensions
    red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
    green_fill = PatternFill(start_color="00FF00", end_color="00FF00", fill_type="solid")
    yellow_fill = PatternFill(start_color="FFFF00", end_color="FFFF00", fill_type="solid")

    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=ws.max_column):

        for cell in row:
            if cell.column_letter in ["A", "B"]:
                # dv.add(cell)
                if cell.value == "no":
                    cell.fill = red_fill
                elif cell.value == "yes" or cell.value == "maybe+":
                    cell.fill = green_fill
                elif cell.value not in ["yes", "no"]:
                    cell.fill = yellow_fill
            if cell.column_letter == "F":
                cell.hyperlink = cell.value
                cell.style = "Hyperlink"

    wb.save(excel_file)


def general_scrape_and_ai(unique_urls, assistant):
    new_data = [0]
    new_df = pd.DataFrame(columns=required_columns)
    offset = 0
    while len(
            new_data) > 0:  # running in loop until scraping all data (in case that it blocked in middle of scraping by linkdein etc)
        try:
            print(f"offset:  {offset}")
            new_data = scrape_all_jobs(os.getenv('sites'), os.getenv('search_term'), os.getenv('location'),
                                       os.getenv('hours_old'),
                                       os.getenv('results_wanted'), offset)
            # new_data = pd.read_csv("temp.csv")
            print(f"len(new_data): {len(new_data)}")
            # new_data.to_csv(f"temp{offset}.csv", index=False)
        except Exception as e:
            print(f"Error while scraping data: ,{str(e)}")
            new_data = pd.DataFrame(columns=required_columns)
        for index, row in new_data.iterrows():
            if row['job_url'] not in unique_urls:
                try:
                    unique_urls.add(row['job_url'])
                    msg = f"title: {row['title']}. description: {row['description']}"

                    ai_recommend = assistant.submit_message(msg)
                    # print(ai_recommend)
                    recommendation, explanation = split_string(ai_recommend)
                    new_row = {
                        "applied": "",
                        "AI_recommendation": recommendation,
                        "AI_explanation": explanation,

                        "company": row['company'],
                        "title": row['title'],
                        "link": row['job_url'],
                        "description": row['description'],
                        "posted_date": row['date_posted'],
                        "scrape_date": date.today(),

                    }
                    new_df.loc[len(new_df)] = new_row
                    new_row_df = pd.DataFrame([new_row])
                    new_row_df.to_csv(f"after_ai_temp.csv", mode='a', index=False, header=False)
                except Exception as e:
                    print(f"Error while sending to gpt: ,{str(e)}")
        offset += len(new_data)
        break  # stop the loop

    return new_df


def main():
    load_env_file('.env')
    data = load_df()
    unique_urls = set(data["link"])
    assistant_name = "MyJobsMatcher"
    with open('instructions.txt', 'r',encoding='utf-8') as file:
        instructions = file.read()
    assistant = OpenAIAssistant(os.getenv('api_key'), assistant_name, instructions, os.getenv('model'),
                                os.getenv('assistant_id'))
    print(assistant.assistant_id) # for using the same assistant for the next round
    new_df = general_scrape_and_ai(unique_urls, assistant)
    df = pd.concat([data, new_df])
    df.to_excel(excel_file, index=False, engine='openpyxl')
    beautify_excel()


if __name__ == "__main__":
    main()
