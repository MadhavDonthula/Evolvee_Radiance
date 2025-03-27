# Evolvée Radiance Website Setup Guide

This guide will walk you through the steps to set up and run the Evolvée Radiance website, an online cosmetics platform.

## Prerequisites

Before starting, ensure you have the following installed:

- Python 3.x
- Django (Install via `pip install django`)
- A virtual environment setup (Optional but recommended)

## Setup Instructions

### 1. Activate the Virtual Environment (If Applicable)

#### Windows (cmd or PowerShell):
`venv\Scripts\activate`

#### Mac/Linux:
`source venv/bin/activate`

### 2. Navigate to the Evolvée Radiance Project Directory
Ensure you are in the project folder where **manage.py** is located.

### 3. Install Dependencies (If Applicable)
If this is your first time setting up the project, you may need to install any required dependencies listed in the requirements.txt file. Run the following command to install them:  

`pip install -r requirements.txt`

### 4. Run Database Migrations (If Needed)
If this is your first time running the website, or if there have been changes to the database, run the following command to apply the necessary migrations:  

`python manage.py migrate`

### 5. Start the Development Server
To start the development server and view the website, run:   

`python manage.py runserver`  

By default, the server runs on http://127.0.0.1:8000/ (localhost). You can preview the site by opening this URL in your browser.

## Authors
This project was developed by:  

Madhav Donthula  
Umniyah Mohammed  

For any inquiries or questions, you can reach out at:

Email: umniyah.mohammed@gmail.com  
GitHub: [UMNIYAH](https://github.com/UMNIYAH)


---
This version includes a reference to the Evolvée Radiance project and its purpose. If you have any specific configurations or additional website requirements, you can add those to the `README.md` as well!
