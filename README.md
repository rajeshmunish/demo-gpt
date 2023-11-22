# UBTI Demo GPT

This project showcases the capabilities of combining OpenAI's GPT-4 with Streamlit to generate SQL queries based on natural language input. Users can enter a message describing the data they want to query from an SQLite database, and the application will display the generated SQL query as well as the results from the database.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)


## Features

- **Natural Language to SQL**: Uses GPT-4 to transform user's natural language input into an SQL query or details based on the request.
- **Streamlit Interface**: Provides a simple and intuitive interface for users to input their queries.
- **SQL Server Backend**: Uses SQL Server as the database backend to store and query any data.
  
## Prerequisites

- Python 3.6 or above
- Virtual Environment (recommended)

## Installation

2. **Set up a Virtual Environment** (optional but recommended):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
    ```

3. **Install the Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up Environment Variables**:
   
   Imake sure you have the credentials set up as environment variables or stored safely.

## Usage

1. **Run the Streamlit App**:
    ```bash
    streamlit run main_app.py
    ```

2. Open the displayed URL in your browser, usually `http://localhost:8501`.

3. Type in your natural language query into the input box, like "List out all the applications".

4. View the generated SQL query and the results from the database.


