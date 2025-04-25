# Domain Authority

## Project Overview

**Domain Authority** is a web application that automates the process of scraping domain names from a domain auction website, storing them in a MySQl database and Google Spreadsheets, and then fetching domain authority metrics using the Moz API. The project is built with **Python** as the backend and **React** as the frontend.

### Key Features

* **Domain Scraping** : Automatically scrapes domain names from the auction website [https://whc.ca/domain-names/auctions/](https://whc.ca/domain-names/auctions/).
* **Data Storage** : Saves the scraped domain names to a MySQl database and Google Spreadsheets.
* **Domain Authority Fetching** : Uses the Moz API to fetch domain authority metrics (e.g., Domain Authority, Page Authority, etc.) for the scraped domains.
* **User Interface** : A React-based frontend to display the scraped domains and their metrics.


## Technologies Used

### Backend (Python)

* **Web Scraping** : `BeautifulSoup`, `requests`, or `Scrapy` for scraping domain names.
* **Database** : `SQLite`, `PostgreSQL`, or any preferred database to store domain data.
* **Google Sheets API** : `gspread` or `Google API Client` to interact with Google Spreadsheets.
* **Moz API** : `requests` or `mozapi` to fetch domain authority metrics.
* **Framework** : `Flask`  for backend API development.

### Frontend (React)

* **UI Framework** : React.js for building the user interface.
* **State Management** : `Redux` or `Context API` for managing application state.
* **Styling** : `CSS`, `Sass`, or libraries like `Material-UI` or `TailwindCSS`.
* **API Integration** : `Axios` or `Fetch` to communicate with the backend.





## API Endpoints

### Backend API

* `POST /fetch_url_metrics_csv`: Fetch domain authority metrics for all domains uploaded as xlsx or csv
* GET /start-scrape `: Trigger domain scraping.

## Usage

1. **Scrape Domains** :

* The backend will automatically scrape domains from the auction website and save them to the database and Google Spreadsheets.

1. **Fetch Domain Authority** :

* The backend will use the Moz API to fetch domain authority metrics for the scraped domains.

1. **View Results** :

* Use the React frontend to view the scraped domains and their metrics in a user-friendly interface.


## Setup Instructions

### **Prerequisites:**

### **1. XAMPP Server (for MySQL)**

XAMPP is a free and open-source cross-platform web server solution stack package developed by Apache Friends, which includes MySQL.

#### **Steps to Install XAMPP:**

1. **Download XAMPP:**
   * Visit the official XAMPP website: [https://www.apachefriends.org/index.html](https://www.apachefriends.org/index.html).
   * Download the installer for your operating system (Windows, macOS, or Linux).
2. **Install XAMPP:**
   * Run the installer and follow the on-screen instructions.
   * During installation, ensure that **MySQL** is selected as one of the components to install.
3. **Start MySQL:**
   * After installation, open the XAMPP Control Panel.
   * Start the **MySQL** service by clicking the "Start" button next to it.
4. **Access MySQL:**
   * You can access MySQL via phpMyAdmin (included in XAMPP) by navigating to `http://localhost/phpmyadmin` in your browser.
   * Alternatively, use the MySQL command-line tool.

---

### **2. Python**

Python is required for running Python-based applications or scripts.

#### **Steps to Install Python:**

1. **Download Python:**
   * Visit the official Python website: [https://www.python.org/downloads/](https://www.python.org/downloads/).
   * Download the latest version of Python for your operating system.
2. **Install Python:**
   * Run the installer and ensure you check the box to **Add Python to PATH** during installation.
   * Complete the installation process.
3. **Verify Installation:**
   * Open a terminal or command prompt and run:
     bash

     Copy

     ```
     python --version
     ```
   * This should display the installed Python version.

---

### **3. Node.js (Version 22.14.0)**

Node.js is required for running JavaScript-based applications or scripts.

#### **Steps to Install Node.js:**

1. **Download Node.js:**
   * Visit the official Node.js website: [https://nodejs.org/](https://nodejs.org/).
   * Download the specific version **22.14.0** for your operating system.
2. **Install Node.js:**
   * Run the installer and follow the on-screen instructions.
   * Ensure that the option to add Node.js to your system's PATH is selected.
3. **Verify Installation:**
   * Open a terminal or command prompt and run:
     bash

     Copy

     ```
     node --version
     ```
   * This should display `v22.14.0` as the installed version.
4. **Install npm (Node Package Manager):**
   * npm is included with Node.js. Verify its installation by running:
     bash

     Copy

     ```
     npm --version
     ```

---

### **Summary of Prerequisites**

| **Tool**    | **Version** | **Installation Steps**                                                         |
| ----------------- | ----------------- | ------------------------------------------------------------------------------------ |
| **XAMPP**   | Latest            | Download from[Apache Friends](https://www.apachefriends.org/index.html), install MySQL. |
| **Python**  | Latest            | Download from[Python.org](https://www.python.org/downloads/), add to PATH.              |
| **Node.js** | v22.14.0          | Download from[Node.js](https://nodejs.org/), install and verify version.                |

### Backend Setup

### 1. Install Python Dependencies

First, ensure you have all the necessary Python packages installed by running:

```
pip install -r requirements.txt
```

### 2. Set Up XAMPP and MySQL Database

Before running the backend server, you need to set up the MySQL database using XAMPP.

#### Step 1: Start XAMPP

* Download and install [XAMPP](https://www.apachefriends.org/index.html) if you haven't already.
* Launch the XAMPP Control Panel.
* Start the `Apache` and `MySQL` services by clicking the "Start" button next to each.

#### Step 2: Create the Database

* Open your web browser and go to `http://localhost/phpmyadmin`.
* In the phpMyAdmin interface, click on the "Databases" tab.
* Create a new database named `domain`.

### 3. Run the Backend Server

Once the database is set up, you can start the backend server:

```
python api.py
```

This will start your backend server, which should now be able to connect to the MySQL database you created.

### Additional Notes:

* Ensure that your `api.py` script is configured to connect to the MySQL database using the correct credentials (username, password, host, etc.).
* If you encounter any issues, check the logs for errors related to database connectivity and ensure that XAMPP's MySQL service is running.

### Frontend Setup

1. Navigate to the `frontend` directory:

   ```
   cd ../frontend
   ```
2. **Install Node.js dependencies** :

```
   npm install
```

1. **Start the React development server** :

```
   npm start
```

1. Open your browser and visit `http://localhost:3000` to view the application.
