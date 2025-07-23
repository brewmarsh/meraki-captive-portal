# 📝 Requirements Document

This document outlines the functional and non-functional requirements for the Meraki Captive Portal application.

## 1. Functional Requirements

### 1.1. Splash Page

-   **FR1.1.1:** The system shall display a splash page to users connecting to the guest Wi-Fi network.
-   **FR1.1.2:** The splash page shall require users to log in before they can access the internet.
-   **FR1.1.3:** The system shall provide a registration page for new users.
-   **FR1.1.4:** The splash page shall display a customizable logo.
-   **FR1.1.5:** The splash page shall feature a "Connect" button that grants the user internet access.
-   **FR1.1.6:** The splash page shall include a timer that automatically redirects the user to their original destination.

### 1.2. Client Data Capture

-   **FR1.2.1:** The system shall capture the client's MAC address, IP address, and browser user agent.
-   **FR1.2.2:** The captured client data shall be stored in a persistent database.
-   **FR1.2.3:** The system shall record the timestamp of the client's first connection.
-   **FR1.2.4:** The system shall update a "last seen" timestamp for returning clients.

### 1.3. Admin Dashboard

-   **FR1.3.1:** The system shall provide a web-based admin dashboard.
-   **FR1.3.2:** The admin dashboard shall display the total number of connected clients.
-   **FR1.3.3:** The admin dashboard shall display a list of recently connected clients.
-   **FR1.3.4:** The admin dashboard shall display the status of the Meraki API integration.
-   **FR1.3.5:** The admin dashboard shall allow the user to force a refresh of the page.
-   **FR1.3.6:** The admin dashboard shall allow the user to set the auto-refresh interval.
-   **FR1.3.7:** The admin dashboard shall display charts for connections per day and top user agents.

### 1.4. Meraki Integration

-   **FR1.4.1:** The system shall integrate with the Meraki Dashboard API.
-   **FR1.4.2:** The system shall verify that the necessary port forwarding rule is active on the Meraki network.
-   **FR1.4.3:** The system shall verify that the splash page URL is correctly set for the specified SSIDs.
-   **FR1.4.4:** The system shall provide a detailed Meraki status page.

## 2. Non-Functional Requirements

### 2.1. Performance

-   **NFR2.1.1:** The splash page shall load quickly to provide a seamless user experience.
-   **NFR2.1.2:** The application shall be able to handle a high volume of concurrent connections.
-   **NFR2.1.3:** Database queries shall be optimized to ensure fast retrieval of client data.
-   **NFR2.1.4:** The application shall cache the Meraki status data to improve performance.

### 2.2. Security

-   **NFR2.2.1:** Access to the admin dashboard shall be restricted to a configurable IP subnet.
-   **NFR2.2.2:** The application shall not store any personally identifiable information (PII).
-   **NFR2.2.3:** The application shall log all security-related events.
-   **NFR2.2.4:** The application shall use environment variables to manage sensitive information.
-   **NFR2.2.5:** The application shall have custom error pages for 404 and 500 errors.
-   **NFR2.2.6:** The application shall be protected against common web vulnerabilities (e.g., XSS, CSRF).
-   **NFR2.2.7:** The application shall use a strong password hashing algorithm.

### 2.3. Usability

-   **NFR2.3.1:** The splash page shall have a clean and intuitive design.
-   **NFR2.3.2:** The admin dashboard shall provide a clear and concise overview of the system's status.
-   **NFR2.3.3:** The Meraki status page shall provide detailed and easy-to-understand information.
-   **NFR2.3.4:** The admin dashboard shall have a dark mode option.
-   **NFR2.3.5:** The application shall display a loading screen while the page is initializing.

### 2.4. Deployment and CI/CD

-   **NFR2.4.1:** The application shall be containerized using Docker.
-   **NFR2.4.2:** The application shall use Docker Compose for local development.
-   **NFR2.4.3:** The application shall include a CI/CD workflow for automated linting, testing, and versioning.
-   **NFR2.4.4:** The CI/CD workflow shall include a step to scan the Docker image for vulnerabilities.
-   **NFR2.4.5:** The CI/CD workflow shall enforce code quality standards.
-   **NFR2.4.6:** The CI/CD workflow shall include static type checking.

### 2.5. Customization

-   **NFR2.5.1:** The application's logo, styling, and timer duration shall be easily customizable.
-   **NFR2.5.2:** The application's configuration shall be managed through environment variables.

### 2.6. Reliability and Quality

-   **NFR2.6.1:** The application shall be robust and handle unexpected errors gracefully.
-   **NFR2.6.2:** The application shall include a comprehensive test suite with high code coverage.
-   **NFR2.6.3:** The codebase shall adhere to the PEP 8 style guide.
-   **NFR2.6.4:** The application shall include a mechanism for database migrations.
-   **NFR2.6.5:** The system shall handle API errors gracefully and log them appropriately.
-   **NFR2.6.6:** The system shall implement a retry mechanism for transient API errors.
-   **NFR2.6.7:** The synchronization process shall be idempotent.

### 2.7. Documentation

-   **NFR2.7.1:** The project shall have a clear and comprehensive `README.md` file.
-   **NFR2.7.2:** The project shall have a `DEVELOPERS.md` file with instructions for setting up a development environment.
-   **NFR2.7.3:** The project shall have a `REQUIREMENTS.md` file that is kept up-to-date.
-   **NFR2.7.4:** The project shall have a `DEPENDENCIES.md` file that lists all the project's dependencies.
-   **NFR2.7.5:** The code shall be well-documented with comments and docstrings.

## 3. Future Work

This section outlines potential future enhancements and new features for the Meraki Captive Portal project.

### 3.1. High Priority

-   [ ] **Implement a more robust testing suite:** Add more tests to cover all the application's features, including the Meraki API integration.
-   [ ] **Add support for more authentication methods:** Implement support for other authentication methods, such as social logins (Google, Facebook, etc.) or email/password authentication.
-   [ ] **Improve error handling:** Add more specific error handling to provide better feedback to the user and to make debugging easier.

### 3.2. Medium Priority

-   [ ] **Implement a multi-stage Docker build:** Reduce the production image size by implementing a multi-stage Docker build.
-   [ ] **Add a dark mode:** Add a dark mode option to the web interface.
-   [ ] **Implement a more advanced admin dashboard:** Add more features to the admin dashboard, such as charts and graphs to visualize the captured data.
-   [ ] **Add support for multiple languages:** Add support for multiple languages to the web interface.

### 3.3. Low Priority

-   [ ] **Add a "remember me" feature:** Add a feature to remember users so they don't have to go through the splash page every time they connect to the Wi-Fi network.
-   [ ] **Add a "terms of service" page:** Add a page with the terms of service that users must accept before connecting to the Wi-Fi network.
-   [ ] **Add a "privacy policy" page:** Add a page with the privacy policy to inform users about how their data is collected and used.
