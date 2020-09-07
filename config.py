# Make shift argument parser

from googleapiclient.discovery import build

from creds import authenticate_creds

# Change the following to your test requirements
# ================================
# spreadsheetId = '1aUwUL99-FHfH0NdbxfGW886sqSEXVU2yVBOXAJf2RXc'
# Leave empty if you want a new spreadsheet to be created.
spreadsheetId = ''
spreadsheet_name = 'AWS rhel 8.2 report' 
OS_RELEASE = '8.2'

test_name = ''
test_path = ''

system_name = ''
region = 'US East (N. Virginia)'
cloud_type = 'AWS'
# ================================

creds = authenticate_creds()
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()
