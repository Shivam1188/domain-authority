from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
import gspread
from google.oauth2.service_account import Credentials
# Set up MySQL and SQLAlchemy
DATABASE_URI = 'mysql+mysqlconnector://root:@localhost/domain'  # Change with your database credentials
Base = declarative_base()
# Define the DomainName class (ORM)
class DomainName(Base):
    __tablename__ = 'domain_names'  # Table name in the database
    
    # Define the id column to be auto-incremented
    id = Column(Integer, primary_key=True, autoincrement=True)  # Automatically increment the primary key
    domain = Column(String(255), unique=True, nullable=False)

# Create a new database session
engine = create_engine(DATABASE_URI)
Base.metadata.create_all(engine)  # Create the table in MySQL (if it doesn't exist)
Session = sessionmaker(bind=engine)
session = Session()
# Set up Google Sheets API
def setup_google_sheets():
    # Define the scope
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # Load credentials from the JSON file
    # creds = Credentials.from_service_account_file(r"C:\Users\PC\Desktop\New folder\cred.json", scopes=scope)
    # Authorize the client
    creds = Credentials.from_service_account_file(r"cred.json", scopes=scope)
    client = gspread.authorize(creds)
    # Open the spreadsheet by URL
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1zgohni2jlZNw7ybXeSTvJ2kb4mBGRGl6OLqpP-VyRQM/edit?usp=sharing"  # Replace with your spreadsheet URL
    sheet = client.open_by_url(spreadsheet_url).sheet1  # Use the first sheet
    return sheet

# Set up Chrome options
options = webdriver.ChromeOptions()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# Initialize the WebDriver (Chrome in this case)
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Go to the URL you want to scrape
url = "https://whc.ca/domain-names/auctions/"  # Replace with the URL of the website you want to scrape
driver.get(url)
wait = WebDriverWait(driver, 10)

# Wait for the page to load
time.sleep(5)

# # Set up Google Sheets
sheet = setup_google_sheets()

try:
    # Locate and click the "Accept All" button (cookie acceptance or pop-up)
    accept_all_button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-cky-tag="accept-button"]')))
    accept_all_button.click()

    # Locate and interact with the "per-page" dropdown (pagination option)
    dropdown = Select(driver.find_element(By.ID, "per-page"))
    dropdown.select_by_value("100")  # Select the option with value "100" (adjust based on available options)
    time.sleep(5)  # Allow the page to refresh with new settings

    while True:
        # Extract domain names
        domainname_elements = driver.find_elements(By.XPATH, "//div[@domainname]")
        domainnames = [element.get_attribute('domainname') for element in domainname_elements]
        
        # Save domain names to Google Sheet
        rows_to_add = [[domain] for domain in domainnames]
        print(rows_to_add)
        # # Append multiple rows at once
        sheet.append_rows(rows_to_add)  # Append the list of ro
        print("Domain names saved to Google Sheet.")
        rows_to_add = [DomainName(domain=domain) for domain in domainnames]
        session.add_all(rows_to_add)
        session.commit()  # Commit the session to MySQL
        print(f"Domain names saved to MySQL: {domainnames}")
        # Check if the "Next" button is available
        try:
            next_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@class='page-link' and @aria-label='Next']")))
            next_button.click()
            print("Navigated to the next page.")
            time.sleep(10)  # Wait for the next page to load
        except Exception as e:
            print(f"Next button is disabled or not found. Error: {e}. Exiting the loop.")
            break  # Exit the loop if no next button is found

except Exception as e:
    print("An error occurred:", e)

finally:
    # Close the browser
    driver.quit()
