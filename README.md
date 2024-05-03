# YouTube Data Harvesting and Warehousing

The Youtue Data Harvesting and Warehousing is an application built on streamlit framework that allows users to access and analyze data from multiple YouTube channels.

This page contains information about gettng started.

## Pre-requisites:
- Python version 3.8 above
- Python environment manager (comes with python) - venv
- Python package manager (comes with python) - pip
- MacOs: Xcode command line tools
- VS Code
- Setup Google API:
    - Create a project on the [Google Cloud Console](https://console.cloud.google.com)
    - Navigate and enable the `YouTube Data API v3` service
    - Create API key Credentials

## Installation steps:

Step 1: Make sure you are in project folder `youtube-project` or navigate to the folder 
`cd youtube-project`

Step 2: Create a directoty to install virtual environment and its dependencies
`python -m venv .venv`

Step 3: Activate the environment
```
# Windows command prompt
.venv\Scripts\activate.bat

# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS and Linux
source .venv/bin/activate
```

Step 4: Once activated, you will see your environment name in parentheses before your prompt. `(.venv)`

Step 5: Run the below command to set environment variable
```
export API_KEY=your_youtube_api_key
export MYSQL_USERNAME=your_sql_username
export MYSQL_PASSWORD=your_sql_password
export MONGO_USERNAME=your_mongodb_user_name
export MONGO_PASSWORD=your_mongodb_password
```

Step 5: Install python packages
``` pip install streamlit pandas mysql-connector-python google-api-python-client pymongo[srv] ```

Step 6: Run the Youtube data harvesting app
``` streamlit run youtube_app.py ```

Step 7: Decativate the environment by running ```deactivate```