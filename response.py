from google.oauth2 import service_account
from googleapiclient.discovery import build
from flask import Flask, jsonify, request
import time
from flask_sqlalchemy import SQLAlchemy
import requests
import pandas as pd
from dotenv import load_dotenv
import os
from api import db,PageData

# Path to your service account JSON key file
SERVICE_ACCOUNT_FILE = 'cred.json'
load_dotenv()
# Define the scope
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

api_key = os.getenv("API_KEY")

# ID of the Google Spreadsheet (found in the URL)
SPREADSHEET_ID = "1zgohni2jlZNw7ybXeSTvJ2kb4mBGRGl6OLqpP-VyRQM"  # Only the ID, not the full URL

def fetch_google_sheet_data():
    # Authenticate using the service account
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

    # Build the service
    service = build('sheets', 'v4', credentials=creds)

    # Call the Sheets API
    sheet = service.spreadsheets()
    RANGE_NAME = 'Sheet1'  # Replace with your sheet name or range (e.g., 'Sheet1!A1:D10')
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
    
    # Get the values
    values = result.get('values', [])
    flattened_data = [item[0] for item in values]
    print(flattened_data)

    if not values:
        print('No data found.')
    else:
        for row in values:
            print(row)
            

            
def fetch_url_metrics_csv():
    try:
        fetch_google_sheet_data
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

if __name__ == '__main__':
    fetch_google_sheet_data()