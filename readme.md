# Job Scraper with AI Filtering

This project enables you to scrape job postings from LinkedIn, Glassdoor, Indeed, and ZipRecruiter. The job descriptions are sent to an AI LLM model to determine their suitability for you and organize all jobs for you in Excel file.

## Features

- **Multi-platform Job Scraping:** Automatically scrape jobs from LinkedIn, Glassdoor, Indeed, and ZipRecruiter.
- **AI-based Filtering:** The scraped job descriptions are sent to an AI model for evaluation based on your predefined criteria.
- **Duplicate Prevention:** Built-in mechanism to prevent sending the same job to the AI more than once.
- **Simple and Adjustable:** The code is straightforward and easy to modify to suit your needs.

## Installation

1. **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```
   
2. **Obtain OpenAI API Key:**
    - Get your [OpenAI API key](https://platform.openai.com/account/api-keys).

3. **Create a `.env` file:**
    - Use the `.env-example` file provided as a template.
    - Replace the placeholders with your actual values.

4. **Write Instructions for the AI:**
    - Write your criteria or preferences for the AI in the `instructions.txt` file.
    - An example is provided in the `instructions-example.txt` file.

## Usage

1. **Run the scraping and AI filtering process:**
    ```bash
    python jobs.py
    ```

2. **Output:**

   The results will be saved in an `jobs.xlsx` file in the project directory.
   ![img.png](img.png)

## Notes

- Make sure your `.env` and `instruction.txt` files are properly configured before running the script.
- You can reuse the AI assistant in your project by printing the assistant instance ID in [main function](https://github.com/elchananvol/AIJobScraper/blob/d151e1492b591b4e73579ebe1dcb74f452e8dc08/jobs.py#L131) for the first time and then configur it in the `.env` file for the next running.
- The project is designed to be easily customizable, so feel free to adjust the scraping and filtering logic as needed.

## Support

If you found this project helpful, please consider giving it a ⭐ on GitHub. Your support is much appreciated!

If you'd like to buy me a coffee, you can do so [here](https://ko-fi.com/C0C2125R0E). ☕