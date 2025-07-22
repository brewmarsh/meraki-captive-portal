# 📝 Requirements Document

This document outlines the functional and non-functional requirements for the Meraki Captive Portal application.

## 1. Functional Requirements

### 1.1. Splash Page

-   **FR1.1.1:** The system shall display a splash page to users connecting to the guest Wi-Fi network.
-   **FR1.1.2:** The splash page shall require users to log in before they can access the internet.
-   **FR1.1.3:** The system shall provide a registration page for new users.
-   **FR1.1.4:** The splash page shall display a customizable logo. The default logo is located at `app/static/images/logo.png`.
-   **FR1.1.5:** The splash page shall feature a "Connect" button that, when clicked, grants the user internet access by redirecting them to the Meraki-provided `base_grant_url`.
-   **FR1.1.6:** The splash page shall include a timer that automatically redirects the user to their original destination after a configurable amount of time.

### 1.2. Client Data Capture

-   **FR1.2.1:** The system shall capture the client's MAC address, IP address, and browser user agent from the query parameters provided by Meraki.
-   **FR1.2.2:** The captured client data shall be stored in a persistent PostgreSQL database.
-   **FR1.2.3:** The system shall record the timestamp of the client's first connection.
-   **FR1.2.4:** The system shall update a "last seen" timestamp for returning clients.

### 1.3. Admin Dashboard

-   **FR1.3.1:** The system shall provide a web-based admin dashboard accessible only from a configurable IP subnet.
-   **FR1.3.2:** The admin dashboard shall display the total number of connected clients.
-   **FR1.3.3:** The admin dashboard shall display a list of the 10 most recently connected clients, including their MAC address, IP address, user agent (truncated), and last seen time.
-   **FR1.3.4:** The admin dashboard shall display the status of the Meraki API integration, including the organization ID, SSID names, external URL, and whether the port forwarding rule and splash page are correctly configured.
-   **FR1.3.5:** The admin dashboard shall allow the user to force a refresh of the page.
-   **FR1.3.6:** The admin dashboard shall allow the user to set the auto-refresh interval.
-   **FR1.3.7:** The admin dashboard shall display charts for connections per day and top user agents.

### 1.4. Meraki Integration

-   **FR1.4.1:** The system shall integrate with the Meraki Dashboard API to automatically configure the splash page URL for one or more SSIDs.
-   **FR1.4.2:** The system shall verify that the necessary port forwarding rule is active on the Meraki network.
-   **FR1.4.3:** The system shall verify that the splash page URL is correctly set for the specified SSIDs.
-   **FR1.4.4:** The system shall provide a detailed Meraki status page showing the status of the API key, organization ID, SSID names, external URL, port forwarding rule, and splash page configuration.

## 2. Non-Functional Requirements

### 2.1. Performance

-   **NFR2.1.1:** The splash page shall load quickly to provide a seamless user experience.
-   **NFR2.1.2:** The application shall be able to handle a high volume of concurrent connections without significant degradation in performance.
-   **NFR2.1.3:** Database queries shall be optimized to ensure fast retrieval of client data for the admin dashboard.
-   **NFR2.1.4:** The application shall cache the Meraki status data to improve performance.

### 2.2. Security

-   **NFR2.2.1:** Access to the admin dashboard shall be restricted to a configurable IP subnet using the `X-Forwarded-For` header to identify the client's IP address.
-   **NFR2.2.2:** The application shall not store any personally identifiable information (PII) other than the client's MAC address, IP address, and user agent.
-   **NFR2.2.3:** The application shall log all connection errors and security-related events to a file for debugging and auditing purposes.
-   **NFR2.2.4:** The application shall use environment variables to manage sensitive information such as API keys and database credentials.
-   **NFR2.2.5:** The application shall have custom error pages for 404 and 500 errors.

### 2.3. Usability

-   **NFR2.3.1:** The splash page shall have a clean and intuitive design that is easy for users to navigate.
-   **NFR2.3.2:** The admin dashboard shall provide a clear and concise overview of the system's status and client data.
-   **NFR2.3.3:** The Meraki status page shall provide detailed and easy-to-understand information about the Meraki integration.
-   **NFR2.3.4:** The admin dashboard shall have a dark mode option.
-   **NFR2.3.5:** The application shall display a loading screen while the page is initializing.

### 2.4. Deployment

-   **NFR2.4.1:** The application shall be containerized using Docker for easy and consistent deployment. The Docker image shall be optimized for size and security by using a multi-stage build and running as a non-root user.
-   **NFR2.4.2:** The application shall use Docker Compose to manage the application and database containers in a development environment.
-   **NFR2.4.3:** The application shall include a CI/CD workflow for automated linting, testing, and versioning.
-   **NFR2.4.4:** The CI/CD workflow shall include a step to scan the Docker image for known vulnerabilities.

### 2.5. Customization

-   **NFR2.5.1:** The application's logo, styling, and timer duration shall be easily customizable by modifying the files in the `app/static` directory.
-   **NFR2.5.2:** The application's configuration shall be managed through environment variables as defined in `.env.example`.

### 2.6. Reliability and Quality

-   **NFR2.6.1:** The application shall be robust and handle unexpected errors gracefully without crashing.
-   **NFR2.6.2:** The application shall include a comprehensive test suite with high code coverage to ensure the correctness of its features.
-   **NFR2.6.3:** The codebase shall adhere to the PEP 8 style guide for Python code.
-   **NFR2.6.4:** The application shall include a mechanism for database migrations to manage changes to the database schema.
-   **NFR2.6.5:** The CI/CD pipeline shall enforce code quality standards through automated linting and static analysis. The pipeline shall use `flake8` for linting, `black` for code formatting, `isort` for import sorting, `bandit` for security analysis, and `mypy` for static type checking.

## 3. TODO

-   **TODO3.3:** Enhance the admin dashboard with data visualization features.
-   **TODO3.4:** Implement internationalization (i18n) for the user-facing pages.
-   **TODO3.6:** Configure the Docker container to run as a non-root user to improve security.
-   **TODO3.7:** Add a Dockerfile linter (e.g., Hadolint) to the CI/CD pipeline.
-   **TODO3.8:** Integrate a vulnerability scanner (e.g., Trivy, Snyk) into the CI/CD pipeline to scan the Docker image for known vulnerabilities.
-   **TODO3.9:** Integrate `black` and `isort` into the CI/CD pipeline to enforce consistent code formatting.
-   **TODO3.10:** Integrate `bandit` into the CI/CD pipeline to perform automated security analysis.
-   **TODO3.11:** Integrate `mypy` into the CI/CD pipeline to perform static type checking.
=======
-   **NFR2.1.2:** The application shall be able to handle a high volume of concurrent connections.

### 2.2. Security

-   **NFR2.2.1:** Access to the admin dashboard shall be restricted to a configurable IP subnet.
-   **NFR2.2.2:** The application shall not store any personally identifiable information (PII) other than the client's MAC address, IP address, and user agent.
-   **NFR2.2.3:** The application shall log all connection errors to a file for debugging purposes.

### 2.3. Usability

-   **NFR2.3.1:** The splash page shall be easy to understand and use.
-   **NFR2.3.2:** The admin dashboard shall provide a clear and concise overview of the system's status.

### 2.4. Deployment

-   **NFR2.4.1:** The application shall be containerized using Docker for easy deployment.
-   **NFR2.4.2:** The application shall use Docker Compose to manage the application and database containers.
-   **NFR2.4.3:** The application shall include a CI/CD workflow for linting and versioning.

### 2.5. Customization

-   **NFR2.5.1:** The application's logo, styling, and timer duration shall be easily customizable.
-   **NFR2.5.2:** The application's configuration shall be managed through environment variables.

## 4. Python Dependencies

The following Python packages are required for the application to run:

-   `Flask>=2.0.0`
-   `python-dotenv>=0.15.0`
-   `Flask-SQLAlchemy>=2.5.0`
-   `Flask-Migrate>=3.0.0`
-   `psycopg2-binary>=2.9.0`
-   `gunicorn>=20.1.0`
-   `meraki>=1.0.0`
-   `Flask-Login>=0.5.0`
-   `Flask-WTF>=1.0.0`
-   `Flask-Caching>=1.10.1`
-   `email-validator>=2.0.0`
