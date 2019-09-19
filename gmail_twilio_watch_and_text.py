from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors
# If modifying these scopes, delete the file token.pickle.
import time
from twilio.rest import Client

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/userinfo.email', 'https://www.googleapis.com/auth/userinfo.profile']

NUMS = ['5555551212', '5555551212']

global FROM
FROM = "+13135551212"       #twilio data 
account_sid = "AAAAAA--sid---AAAAAA"
auth_token = "AAAAAAAA--TOKEN--AAAAAA"
client = Client(account_sid, auth_token)


def show_chatty_threads(service, user_id='me'):
    threads = service.users().threads().list(userId=user_id).execute().get('threads', [])
    for thread in threads:
        tdata = service.users().threads().get(userId=user_id, id=thread['id']).execute()
        
        nmsgs = len(tdata['messages'])  # this is just a count for similiar messages i.e. 3
        #print (nmsgs)

        if nmsgs > 0:    # skip if <3 msgs in thread
            msg = tdata['messages'][0]['payload']
            subject = ''
            for header in msg['headers']:
                if header['name'] == 'Subject':
                    subject = header['value']
                    break
            if "security" in subject:  # looking for text in subject
                for num in NUMS:
                    make_call(num, 'HiFi alert')
                    DelMessagesMatchingQuery(service, user_id='me') #remove msg after 

def DelMessagesMatchingQuery(service, user_id, query=''):
    try:
        response = service.users().messages().list(userId=user_id,
                                            q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, 
            q=query, pageToken=page_token).execute()
            messages.extend(response['messages'])
        else:
            for message in messages:
                message_id = message['id']
                delresponse = service.users().messages().trash(userId=user_id, id=message_id).execute()      
                print(delresponse)
        return messages
    except errors.HttpError as error:
        print('An error occurred: %s' % error)



def make_call(to_number, mesg):
    message = client.messages \
                .create(
                     body=mesg,
                     from_='+13135551212',
                     to=to_number
                 )
    print(message.sid)


def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    while True:
        time.sleep(20)
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first
        # time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        service = build('gmail', 'v1', credentials=creds)
        show_chatty_threads(service)



if __name__ == '__main__':
    main()
