# Meraki Captive Portal

This is a containerized web application for capturing client data from a Meraki guest Wi-Fi network. It features a splash page with a timer, a click-through option, and automatic data capture.

## Features

-   **Client Data Capture:** Automatically captures client MAC address, IP address, and user agent.
-   **Timed Redirect:** Redirects users to their original destination after a 10-second timer.
-   **Click-Through:** Allows users to bypass the timer and connect immediately.
-   **Database Persistence:** Stores captured data in a PostgreSQL database that persists between container runs.
-   **Error Logging:** Logs connection errors to a file.
-   **Containerized:** Runs in a Docker container with a Docker Compose setup for easy deployment.
-   **CI/CD:** Includes a GitHub Actions workflow for linting.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/meraki-captive-portal.git
    cd meraki-captive-portal
    ```
2.  **Create a `.env` file:**
    Copy the example file and update the values for your environment.
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

## Usage

1.  **Configure your Meraki network:**
    -   In your Meraki dashboard, go to **Wireless > Configure > Splash page**.
-   Set the **Custom splash URL** to the address of your running application (e.g., `http://your-server-ip:22787`).
-   For more information on configuring a custom splash URL, see the [Meraki documentation](https://documentation.meraki.com/MR/Splash_Page/Configuring_a_Custom-Hosted_Splash_Page).
    -   Meraki will append query parameters like `client_mac` and `base_grant_url` to this URL.
2.  **Connect a device:**
    -   Connect a device to your guest Wi-Fi network.
    -   The device should be redirected to the captive portal splash page.
    -   The client's data will be captured and stored in the database.

### Meraki API Integration

This application can optionally use the Meraki API to automatically configure the splash page URL for one or more SSIDs. To enable this feature, set the following environment variables in your `.env` file:

-   `MERAKI_API_ENABLED=true`
-   `MERAKI_API_KEY`: Your Meraki API key.
-   `MERAKI_ORG_ID`: Your Meraki organization ID.
-   `MERAKI_SSID_NAMES`: A comma-separated list of SSIDs to apply the splash page to.

When the application starts, it will use the Meraki API to update the splash page settings for the specified SSIDs.

## Customization

-   **Logo:** Replace `app/static/images/logo.png` with your own logo. The recommended size is 150x150 pixels.
-   **Styling:** Modify `app/static/css/style.css` to change the appearance of the splash page.
-   **Timer:** Adjust the timer duration in `app/static/js/main.js`.

## Versioning

This project uses a simplified versioning scheme based on commit messages. When merging a pull request to `main`, include one of the following tags in the commit message:

-   `[major]`: For significant, breaking changes.
-   `[minor]`: For new features or non-breaking changes.
-   `[patch]`: For bug fixes and minor improvements.
