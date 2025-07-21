# 📝 Requirements Document

This document outlines the functional and non-functional requirements for the Meraki Captive Portal application.

## 1. Functional Requirements

### 1.1. Splash Page

-   **FR1.1.1:** The system shall display a splash page to users connecting to the guest Wi-Fi network.
-   **FR1.1.2:** The splash page shall display a customizable logo. The default logo is located at `app/static/images/logo.png`.
-   **FR1.1.3:** The splash page shall feature a "Connect" button that, when clicked, grants the user internet access.
-   **FR1.h4:** The splash page shall include a timer that automatically redirects the user to their original destination after a configurable amount of time.

### 1.2. Client Data Capture

-   **FR1.2.1:** The system shall capture the client's MAC address, IP address, and browser user agent.
-   **FR1.2.2:** The captured client data shall be stored in a persistent database.
-   **FR1.2.3:** The system shall record the timestamp of the client's first connection.
-   **FR1.2.4:** The system shall update a "last seen" timestamp for returning clients.

### 1.3. Admin Dashboard

-   **FR1.3.1:** The system shall provide a web-based admin dashboard accessible only from a configurable IP subnet.
-   **FR1.3.2:** The admin dashboard shall display the total number of connected clients.
-   **FR1.3.3:** The admin dashboard shall display a list of the 10 most recently connected clients, including their MAC address, IP address, and last seen time.
-   **FR1.3.4:** The admin dashboard shall display the status of the Meraki API integration, including the organization ID, SSID names, external URL, and whether the port forwarding rule and splash page are correctly configured.
-   **FR1.3.5:** The admin dashboard shall allow the user to force a refresh of the page.
-   **FR1.3.6:** The admin dashboard shall allow the user to set the auto-refresh interval.

### 1.4. Meraki Integration

-   **FR1.4.1:** The system shall integrate with the Meraki Dashboard API to automatically configure the splash page URL for one or more SSIDs.
-   **FR1.4.2:** The system shall verify that the necessary port forwarding rule is active on the Meraki network.
-   **FR1.4.3:** The system shall verify that the splash page URL is correctly set for the specified SSIDs.

## 2. Non-Functional Requirements

### 2.1. Performance

-   **NFR2.1.1:** The splash page shall load quickly to provide a seamless user experience.
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
