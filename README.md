# Revving Task Project

## Overview

This project is a Django-based application designed for data processing and management. It includes functionality for handling and validating data frames, managing database migrations, and setting up a web server.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Installation

1. Clone the repository to your local machine:

    ```sh
    git clone <repository-url>
    ```

2. Navigate to the project directory:

    ```sh
    cd revvingtask
    ```

3. Create a virtual environment:

    ```sh
    python -m venv venv
    ```

4. Activate the virtual environment:

    - On Windows:

        ```sh
        .\venv\Scripts\activate
        ```

    - On Unix or MacOS:

        ```sh
        source venv/bin/activate
        ```

5. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```

### Running the Application

1. Apply the migrations to create the database schema:

    ```sh
    python manage.py migrate
    ```

2. Start the Django development server:

    ```sh
    python manage.py runserver
    ```

3. The server will start at `http://127.0.0.1:8000/`. You can access the application through your web browser.

## Features

- Data validation and processing using Pandas.
- SQLite database for data persistence.
- ASGI support for asynchronous web applications.

## Project Structure

- `backend/`: Contains Django models, views, and migrations for the application.
- `revvingtask/`: Django project configuration including settings and URL routing.
- `migrations/`: Database migrations scripts.
- `venv/`: Virtual environment for project dependencies.
- `requirements.txt`: List of project dependencies.

## Testing

To run the tests for the application, use the following command:

```sh
python manage.py test
