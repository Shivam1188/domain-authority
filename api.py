from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os
import pandas as pd
import time
from flask_sqlalchemy import SQLAlchemy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import gspread
from google.oauth2.service_account import Credentials
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
import threading

# Initialize the Flask app
app = Flask(__name__)

# Configure the MySQL database connection
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/domain'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
# Load environment variables from .env file
load_dotenv()

class PageData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(255), nullable=False)
    subdomain = db.Column(db.String(255), nullable=False)
    root_domain = db.Column(db.String(255), nullable=False)
    last_crawled = db.Column(db.String(100), nullable=True)
    http_code = db.Column(db.Integer, nullable=True)
    pages_to_page = db.Column(db.Integer, nullable=True)
    nofollow_pages_to_page = db.Column(db.Integer, nullable=True)
    redirect_pages_to_page = db.Column(db.Integer, nullable=True)
    external_pages_to_page = db.Column(db.Integer, nullable=True)
    spam_score = db.Column(db.Integer, nullable=True)
    page_authority = db.Column(db.Integer, nullable=True)
    domain_authority = db.Column(db.Integer, nullable=True)
    link_propensity = db.Column(db.Float, nullable=True)

    def __repr__(self):
        return f"<PageData {self.page}>"

# Enable CORS for all routes
CORS(app)
# Load API Key from environment
api_key = os.getenv("API_KEY")


SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

SERVICE_ACCOUNT_FILE = 'cred.json'

SPREADSHEET_ID = "1yG8r9CAhC3Ms3q624sQvJynuHfTJ1DBgRiJdJq1yx-4"

Base = declarative_base()

class DomainName(Base):
    __tablename__ = 'domain_names'
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain = Column(String(255), nullable=False)

# Set up Google Sheets API
def setup_google_sheets():
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Load credentials from the JSON file
    creds = Credentials.from_service_account_file(r"cred.json", scopes=scope)
    client = gspread.authorize(creds)
    # Open the spreadsheet by URL
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1yG8r9CAhC3Ms3q624sQvJynuHfTJ1DBgRiJdJq1yx-4/edit?gid=0#gid=0"
    sheet = client.open_by_url(spreadsheet_url).sheet1
    return sheet

def start_scraping():
    print("Scraping started!")
    
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-direct-composition")
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--headless")  # Run headless for server environment
    
    # Initialize Chrome WebDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    # Set up Google Sheets
    sheet = setup_google_sheets()
    
    # Go to the URL to scrape
    url = "https://whc.ca/domain-names/auctions/"
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    
    # Wait for the page to load
    time.sleep(5)
    
    total_domains = 0
    page_count = 0
    all_domains = []  # List to store all domain names
    
    try:
        # Accept cookies if needed
        try:
            accept_all_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-cky-tag="accept-button"]')))
            accept_all_button.click()
        except Exception as e:
            print(f"Cookie accept button not found or not clickable: {e}")
        
        # Set pagination to 100 items per page
        dropdown = Select(driver.find_element(By.ID, "per-page"))
        dropdown.select_by_value("100")
        time.sleep(5)
        
        while True:
            page_count += 1
            print(f"Processing page {page_count}")
            
            # Extract domain names
            domainname_elements = driver.find_elements(By.XPATH, "//div[@domainname]")
            domainnames = [element.get_attribute('domainname') for element in domainname_elements]
            
            if not domainnames:
                print("No domains found on this page. Ending scraping.")
                break
                
            # Add domain names to the list
            all_domains.extend(domainnames)
            
            # Save domain names to Google Sheet
            rows_to_add = [[domain] for domain in domainnames]
            sheet.append_rows(rows_to_add)
            
            total_domains += len(domainnames)
            print(f"Added {len(domainnames)} domains. Total domains scraped: {total_domains}")
            
            # Check if there's a next page
            try:
                next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='page-link' and @aria-label='Next']")))
                if "disabled" in next_button.get_attribute("class"):
                    print("Next button is disabled. Scraping completed.")
                    break
                next_button.click()
                print("Navigated to the next page.")
                time.sleep(10)  # Wait for the next page to load
            except Exception as e:
                print(f"No more pages to scrape. Scraping completed.")
                break  # Exit the loop gracefully when no next button is found
    
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
    
    finally:
        driver.quit()
        print("Scraping finished. Browser closed.")
        return {
            "status": "completed",
            "message": f"Scraped {total_domains} domains from {page_count} pages",
            "domains": all_domains  # Include the list of all domains
        }
    
@app.route('/fetch_url_metrics', methods=['POST'])
def fetch_url_metrics():
    try:
        # Get the user input (URL) from the request payload
        data = request.get_json()

        # Ensure 'targets' is part of the incoming request
        if not data or 'targets' not in data:
            return jsonify({"error": "'targets' key is missing in the request"}), 400

        # Extract targets from the user input
        targets = data['targets']
        print(targets)
        # Prepare the request payload in the required format
        request_data = {
            "targets": targets
        }
        # Set the URL for the Moz API
        url = 'https://lsapi.seomoz.com/v2/url_metrics'

        # Set headers
        headers = {
            'x-moz-token': f'{api_key}',
            'Content-Type': 'application/json'  # Ensure the correct content type
        }

        # Send the POST request to the Moz API using the json parameter
        response = requests.post(url, headers=headers, json=request_data)
        time.sleep(10)  
        # Check if the request was successful
        if response.status_code == 200:
            return jsonify(response.json()), 200
        else:
            return jsonify({
                "error": f"Failed to fetch data. Status code: {response.status_code}",
                "message": response.text
            }), 500

    except Exception as e:
        return jsonify({"error": "An error occurred", "message": str(e)}), 500
       
@app.route('/fetch_url_metrics_csv', methods=['POST'])
def fetch_url_metrics_csv():
    try:
        # Get the user input (URL) from the request payload
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']

        # Check if the file has a valid extension
        if file.filename.endswith('.csv'):
            # Read CSV file
            df = pd.read_csv(file)
            
        elif file.filename.endswith('.xlsx'):
            # Read Excel file
            df = pd.read_excel(file)
           
        else:
            return jsonify({"error": "Invalid file type. Only CSV and XLSX files are allowed"}), 400
        
        data_string = df.values.tolist()
     
        flat_list = [item[0] for item in data_string]
        all_responses = []
        chunk_size = 10
        chunks = [flat_list[i:i + chunk_size] for i in range(0, len(flat_list), chunk_size)]
        
        # Prepare the request payload in the required format
        for chunk in chunks:
            print(chunk)
            request_data = {
                "targets": chunk
            }
            # Set the URL for the Moz API
            url = 'https://lsapi.seomoz.com/v2/url_metrics'

            # Set headers
            headers = {
                'x-moz-token': f'{api_key}',
                'Content-Type': 'application/json'  # Ensure the correct content type
            }

            # Send the POST request to the Moz API using the json parameter
            response = requests.post(url, headers=headers, json=request_data)
            
            # Check if the request was successful
            if response.status_code == 200:
                api_response = response.json()
                all_responses.append(response.json())  # Append the response to the list
                # print(f"Response Content: {response.text}")
                
                for record in api_response['results']:
                    page_data = PageData(
                        page=record.get('page', ''),
                        subdomain=record.get('subdomain', ''),
                        root_domain=record.get('root_domain', ''),
                        last_crawled=record.get('last_crawled', ''),
                        http_code=record.get('http_code', None),
                        pages_to_page=record.get('pages_to_page', None),
                        nofollow_pages_to_page=record.get('nofollow_pages_to_page', None),
                        redirect_pages_to_page=record.get('redirect_pages_to_page', None),
                        external_pages_to_page=record.get('external_pages_to_page', None),
                        spam_score=record.get('spam_score', None),
                        page_authority=record.get('page_authority', None),
                        domain_authority=record.get('domain_authority', None),
                        link_propensity=record.get('link_propensity', None)
                 
                    )
                    db.session.add(page_data)
                
                db.session.commit()
                print(f"Response Content: {response.text}")
                time.sleep(10)
            else:
                # If any chunk fails, return the error immediately
                return jsonify({
                    "error": f"Failed to fetch data. Status code: {response.status_code}",
                    "message": response.text
                }), 500

    except Exception as e:
        return jsonify({"error": "An error occurred", "message": str(e)}), 500
    return jsonify(all_responses), 200
    
@app.route('/start-scrape', methods=['GET'])
def api_start_scrape():
    # Run the scraping process synchronously and return the result when completed
    result = start_scraping()
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "up",
        "message": "Service is running"
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables
    app.run(debug=True)
