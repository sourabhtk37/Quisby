from googleapiclient.discovery import build

from util import authenticate_creds

path = 'results_streams_tuned_tuned_virtual-guest_sys_file_none/hawkeye_results'
spreadsheetId = '1aUwUL99-FHfH0NdbxfGW886sqSEXVU2yVBOXAJf2RXc'

test_name = 'stream'
linpack_result_path = 'linpack/perf64.perf.lab.eng.bos.redhat.com.txt'
stream_path = 'results_streams_tuned_tuned_virtual-guest_sys_file_none/m5.24xlarge_results'
system_name = 'perf64'
cloud = 'AWS'

creds = authenticate_creds()
service = build('sheets', 'v4', credentials=creds)

sheet = service.spreadsheets()
