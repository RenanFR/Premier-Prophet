# Premier Prophet

Premier Prophet is a web application designed to visualize predictions of match statistics for football (soccer) fixtures, powered by machine learning. The application fetches fixture data from a backend API and presents it in a user-friendly format, allowing users to explore upcoming matches, teams, and kickoff timings.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)

## Installation
1. Clone the repository: `git clone https://github.com/RenanFR/Premier-Prophet.git`
2. Navigate to the project directory: `cd Premier-Prophet`
3. Install dependencies: `pip install -r requirements.txt`

## Usage
1. **Run the Backend API:**
    - Navigate to the backend directory: `cd backend`
    - Execute: `python backend.py`

2. **Run the Frontend Application:**
    - Navigate to the frontend directory: `cd frontend`
    - Execute: `streamlit run frontend.py`
    - Access the application in your web browser at `http://localhost:8501`.

## Features
- **Upcoming Fixtures:** View a list of upcoming fixtures grouped by date, with details on home teams, away teams, and kickoff timings.
- **User-Friendly Interface:** The application provides an intuitive and easy-to-navigate interface for exploring football fixtures.
