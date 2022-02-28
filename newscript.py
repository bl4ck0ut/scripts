from __future__ import print_function
import pickle
import os


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import time
from twilio.rest import Client

SCOPES = ['https://mail.google.com/']
NUMS = ['1115551212']

global FROM
FROM = "+11115551213"
account_sid = "********sid********"
auth_token = "******* token **********"
client = Client(account_sid, auth_token)

"""Get a list of Messages from the user's mailbox.
"""

def main():

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
            return
        print('Labels:')
        for label in labels:
            print(label['name'])
        print ("Start: %s" % time.ctime())
        time.sleep(10)
        print ("End: %s" % time.ctime())
        show_chatty_threads(service) 


    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
'invalid_scope: Bad Request'
def show_chatty_threads(service, user_id='me'):
    threads = service.users().threads().list(userId=user_id).execute().get('threads', [])
    for thread in threads:
        tdata = service.users().threads().get(userId=user_id, id=thread['id']).execute()
        nmsgs = len(tdata['messages'])

        if nmsgs > 0:    # if there are messages
            msg = tdata['messages'][0]['payload']
            subject = ''
            for header in msg['headers']:
                if header['name'] == 'Subject':
                    subject = header['value']
                    break
            if subject:  # skip if no Subject line
                print('- %s (%d msgs)' % (subject, nmsgs))
                

                if "Alert 1" in subject:  # skip if no Subject line
                    for num in NUMS:
                        make_call(num, 'HiFi alert')
                        DelMessagesMatchingQuery(service, user_id='me')
                        #return show_chatty_threads(service)

                if "Alert 2" in subject:  # skip if no Subject line
                    for num in NUMS:
                        make_call(num, 'HiFi alert')
                        DelMessagesMatchingQuery(service, user_id='me')
                        #return show_chatty_threads(service)
                else:
                    print("no alerting messages")
                    main()
    else:
        print("no messages")
        main()




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
                     from_='+11115551213',
                     to=to_number
                 )
    print(message.sid)




if __name__ == '__main__':
    main()
