from flask import Flask
from .config import Config
from dotenv import load_dotenv
import os
from flask_apscheduler import APScheduler
from apscheduler.executors.pool import ThreadPoolExecutor

# from celery_config import make_celery

scheduler = APScheduler()


def create_app():
    # Load environment variables from .env file
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize APScheduler with Flask app
    app.config["SCHEDULER_API_ENABLED"] = True
    app.config["SCHEDULER_TIMEZONE"] = "America/Los_Angeles"

    # Configure executors with a limited ThreadPoolExecutor (limit to 5 concurrent jobs)
    executors = {
        "default": ThreadPoolExecutor(5),  # Limit to 5 concurrent jobs
    }

    # Add executors to the scheduler
    scheduler.scheduler.configure(executors=executors)

    scheduler.init_app(app)
    scheduler.start()

    # creds = gmail_auth()
    # service = build('gmail', 'v1', credentials=creds)

    # Initialize Celery
    # celery = make_celery(app)

    from .routes import main as main_blueprint

    app.register_blueprint(main_blueprint)

    return app
