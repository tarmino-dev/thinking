# Literature Diary

A minimalistic yet elegant Flask web application designed for writers, readers, and creative thinkers to capture their thoughts, reflections, and inspirations.  
With its warm aesthetic and intuitive interface, Literature Diary blends the charm of traditional journaling with the power of modern web technology.

## Features

- Create, edit, and delete personal notes  
- User authentication (register/login/logout)  
- Clean and cozy interface with warm, book-like tones  
- Contact form with SendGrid email integration  
- Structured templates powered by Flask Blueprints  
- SQLite or PostgreSQL database support  
- Gravatar integration for user avatars  
- Bootstrap 5 and CKEditor for rich-text editing  

## Project Structure

The project follows a modular Flask architecture:

- `app/` — main application package  
  - `routes/` — organized Blueprints (`main`, `auth`, `notes`)  
  - `models/` — SQLAlchemy models  
  - `forms/` — Flask-WTF form definitions  
  - `utils/` — utility functions and decorators (e.g., `admin_only`)  
  - `templates/` — feature-based HTML templates  
  - `static/` — CSS, JS, and image assets  
- `config.py` — environment configuration  
- `main.py` — application entry point  
- `requirements.txt` — dependencies  
- `README.md` — project documentation

## Installation and Setup

### 1. Clone only the `blog_to_deploy` branch

`git clone -b blog_to_deploy https://github.com/tarmino-dev/thinking.git`  
`cd thinking/fun_projects/flask/flask_lit_diary`

### 2. Create and activate a virtual environment

`python3 -m venv venv`  
`source venv/bin/activate`   # on macOS/Linux  
`venv\Scripts\activate`      # on Windows

### 3. Install dependencies

`pip install -r requirements.txt`

### 4. Notes on SendGrid setup

1. Sign up at https://sendgrid.com
2. In your SendGrid dashboard, go to Settings → API Keys and create a new key with “Full Access” or “Mail Send” permissions.
3. Verify your sender identity in Settings → Sender Authentication → Single Sender Verification.
4. The email you verify here must match the value of GMAIL_EMAIL in your environment variables (see below).
5. Once verified, you’ll be able to send emails through your Flask contact form.

### 5. Set environment variables

Environment variables are read from your system configuration, for example from `~/.zshrc` or system environment settings.
Add the following lines to your shell configuration file:

`export FLASK_KEY=your_secret_key`  
`export SQLALCHEMY_DATABASE_URI=sqlite:///literature_diary.db`  
`export GMAIL_EMAIL=your_verified_sender@example.com`  
`export SENDGRID_API_KEY=your_sendgrid_api_key`

After editing, reload your terminal session or run:

`source ~/.zshrc`     # on macOS/Linux

## Run the application

The application is launched by running the main.py file located in the project root.

`python main.py`

Then open your browser and visit:

http://localhost:5000

## Deployment

Literature Diary is optimized for deployment on Render, Railway, or Heroku.

To deploy:

1. Set your environment variables in the hosting service dashboard
2. Push your latest code to the main branch
3. Wait for automatic deployment to complete

## Technologies Used

- Python 3.10+
- Flask
- SQLAlchemy
- Bootstrap 5
- CKEditor
- SendGrid API
- Render (deployment)

## Screenshots

(To be added)

## Author

Literature Diary is developed by tarmino-dev.
Inspired by the timeless art of journaling and the “Blog” project concept from the [100 Days of Python](https://www.udemy.com/course/100-days-of-code/) course, modernized and refactored for production-style readability.

## License

This project is intended for educational and portfolio purposes only.

## Acknowledgements

Special thanks to:

- The Flask and Python community
- Bootstrap and Font Awesome contributors
- The writers and thinkers who inspired this project
