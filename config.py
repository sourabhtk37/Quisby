# Make shift argument parser

from googleapiclient.discovery import build

from util import authenticate_creds

# Change the following to your test requirements
# ================================
spreadsheetId = '1aUwUL99-FHfH0NdbxfGW886sqSEXVU2yVBOXAJf2RXc'
# Leave empty if you want a new spreadsheet to be created.
# spreadsheetId = ""
spreadsheet_name = 'Sample test run' 

test_name = 'uperf'
linpack_result_path = 'linpack/perf64.perf.lab.eng.bos.redhat.com.txt'
stream_path = 'results_streams_tuned_tuned_virtual-guest_sys_file_none/m5.24xlarge_results'
uperf_path = 'uperf_result'

system_name = 'm5.24xlarge'
region = 'US East (N. Virginia)'
cloud_type = 'AWS'
# ================================

creds = authenticate_creds()
service = build('sheets', 'v4', credentials=creds)
sheet = service.spreadsheets()
