# 👩‍💻 Developer Documentation

This document provides information for developers working on the Meraki Captive Portal project.

## 🏗️ Project Architecture

The application is a standard Flask web application with the following structure:

-   `run.py`: The entry point for the Flask application.
-   `app/`: The main application directory.
    -   `__init__.py`: Initializes the Flask application and the database.
    -   `routes.py`: Defines the application's routes, including the splash page, admin dashboard, and API endpoints.
    -   `models.py`: Defines the database models using SQLAlchemy.
    -   `meraki_api.py`: Contains functions for interacting with the Meraki Dashboard API.
    -   `meraki_dashboard.py`: Initializes a shared instance of the Meraki Dashboard API.
    -   `static/`: Contains static assets like CSS, JavaScript, and images.
    -   `templates/`: Contains the HTML templates for the application.
-   `migrations/`: Contains the database migration scripts.
-   `tests/`: Contains the application's tests.
-   `Dockerfile`: Defines the Docker image for the application.
-   `docker-compose.yml`: Defines the Docker Compose setup for running the application and the database.
-   `.env.example`: An example environment file.

## 🛠️ Development Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/meraki-captive-portal.git
    cd meraki-captive-portal
    ```

2.  **Create a `.env` file:**
    Copy the example file and update the values for your development environment.
    ```bash
    cp .env.example .env
    ```

3.  **Build and run the containers:**
    ```bash
    docker-compose up --build
    ```

4.  **Initialize the database:**
    In a separate terminal, run the following command to set up the database tables:
    ```bash
    docker-compose exec web flask db init
    docker-compose exec web flask db migrate -m "Initial migration."
    docker-compose exec web flask db upgrade
    ```

## 🤝 Contributing

We welcome contributions to the Meraki Captive Portal project! To contribute, please follow these steps:

1.  **Fork the repository.**
2.  **Create a new branch for your feature or bug fix.**
3.  **Make your changes and commit them with a descriptive commit message.**
4.  **Push your changes to your fork.**
5.  **Create a pull request to the `main` branch of the original repository.**

When creating a pull request, please make sure to:

-   **Update the `README.md` file if you are adding or changing any features.**
-   **Add or update tests for your changes.**
-   **Follow the existing code style.**

## ✅ Code Style

This project follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code. We use `flake8` to enforce this style. Before submitting a pull request, please make sure to run `flake8` and fix any issues.

## 🧪 Testing

This project uses `pytest` for testing. To run the tests, use the following command:

```bash
docker-compose exec web pytest
```

When adding new features, please make sure to add corresponding tests in the `tests/` directory.
