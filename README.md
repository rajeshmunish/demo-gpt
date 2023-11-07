# UBTI GPT

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Contributing](#contributing)
- [License](#license)

## Features


  
## Prerequisites

- Python 3.6 or above
- Virtual Environment (recommended)

## Installation

1. **Clone the Repository**:
    ```bash
    git clone https://github.com/NikhilSehgal123/Azure-OpenAI-SQL.git
    ```

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
   
   If you're using any external services like Azure or APIs, make sure you have the credentials set up as environment variables or stored safely.

## Usage

1. **Run the Streamlit App**:
    ```bash
    streamlit run demo_gpt.py
    ```

2. Open the displayed URL in your browser, usually `http://localhost:8501`.

3. Type in your natural language query into the input box, like "Show me all expenses greater than 1000".

4. View the generated SQL query and the results from the database.

## How It Works

1. **SQL SERVER Database**:

   The app uses MS SQL to connect the datasbase based on given config. 

2. **Schema Retrieval**:

   Before generating a query, the system retrieves the schema of the table from SQLite to understand its structure.

3. **GPT-4 Model**:

   The main functionality relies on the GPT-4 model to convert a user's natural language input into an SQL query. The app sends a formatted message containing the table's schema to GPT-4, which then returns an appropriate SQL query.

4. **Query Execution**:

   The app then executes the generated SQL query on the sql server database and retrieves the results.




