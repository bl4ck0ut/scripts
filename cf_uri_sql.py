#!/usr/bin/python
#: Title       : Cofense Triage API
#: Date Created: Mon Sep 4th 2019
#: Author      : Charley Pfaff
#: Description : API used to query Cofense to file and database
#
# --------------------------------------------------------------
#
# This script is the primary api file that will write out data based on 
# a query that is selected. This data can be used to query or grep against
# or used to be called with parameters.
# 
# requirnemts:
# Minimal Python libraries including json , triagelib also 
# pip install git+https://github.com/jblackb1/triagelib@master
# 
# example usage: 
# python ./cf_uri_sql.py -p 55555555555555555555555555 -t 05/09/2019T23:00 -u user@company.com -i servername.company.com
#
# What this does is:
# 1.logs into Cofense Triage
# 2.performs a defined search
# 3.returns results to a text file
# 4. delay of 15 seconds between requests to account for Triage request throttling
# -----------------------------------------------------------------------
#
# improvments
# 
# - add alerting to email capability
# - add fields to be reported 
# - read initial rquest and parge last page as loop variable
# 
#
#
# --------------------------------------------------------------
# ChangeLog
# - Located in git history
# --------------------------------------------------------------


from triagelib import TriageSession
import json
import time, sys
import argparse
import sqlite3
from sqlite3 import Error
import datetime 
import os
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email import Encoders


def send_mail(args):

   sender = args.email_sender
   receivers = args.email_rcpt
   message = """From: From sender <sender@ubuntu>
   To: To Person <rcpt.person@todomain.com>
   Subject: New Domains detected
   New domains or URI's detected see attached.
   """

   SUBJECT = "New Phishing domains detected"
   msg = MIMEMultipart()
   msg['Subject'] = SUBJECT
   msg['From'] = sender
   msg['To'] = ', '.join(receivers)
   part = MIMEBase('application', "octet-stream")
   part.set_payload(open(args.uri_file_location, "rb").read())
   Encoders.encode_base64(part)
   part.add_header('Content-Disposition', 'attachment; filename="uri.txt"')
   msg.attach(part)

   try:
      smtpObj = smtplib.SMTP(args.email_forwarder)
      smtpObj.sendmail(sender, receivers, msg.as_string())         
      print "Successfully sent email"
   except:
      print "Error: unable to send email"


def single_query(args):
   triage = TriageSession(host=args.host_name, email=args.username, apikey=args.token)
   if os.path.exists(args.uri_file_location):
       os.remove(args.uri_file_location)
   else:
       print('File does not exists')
   f = open(args.file_location, 'w')
   count=1
   reports = "placeholder"
   while reports and count < 40:
      reports = triage.inbox_reports(start_date=args.start_date, per_page=args.per_page, page=(count))
      conn = sqlite3.connect(args.uri_db_location)
      c=conn.cursor()
      conn.text_factory = str
      time.sleep(15)
      for x in reports:
         cof_urls = x['email_urls']
         for y in cof_urls:
            ct_url = y['url']
            rep_url = x['reported_at']
            rep_sub = x['report_subject']
            #rep_subject = rep_sub.encode('utf-8', 'replace' ).replace("," , "").strip()
            f.write(rep_url.encode('utf-8') + ' , ' 
                    + rep_sub.encode('utf-8').replace("," , "") + ' , ' + ct_url.encode('utf-8') + '\n')
            c.execute("""SELECT uri FROM domains WHERE uri=?""",(ct_url,))
            result = c.fetchone()
            if result:
                pass
            else:
                print "woot new domain"
                print ct_url
                currentDT = datetime.datetime.now()
                c.execute("INSERT INTO domains VALUES (?, ?, ?)", (ct_url, currentDT, rep_sub))
                g = open(args.uri_file_location, 'a')
                g.write(ct_url.encode('utf-8') + ' , '+ (str(currentDT)) + rep_sub.encode('utf-8').replace("," , "") + '\n')
                g.close

      conn.commit()
      conn.close()
      print count
      count += 1
   f.close


def main():
   parser = argparse.ArgumentParser()

   parser.add_argument("-u", "--username", 
        action="store", 
        #action="store",
        help='name of the useraccount to connect')
   parser.add_argument("-p", "--token", 
        action="store",  
        help="the token for the user account")
   parser.add_argument("-i", "--host_name", 
        action="store", 
        help="the Triage that you want to query default:servername.lan")
   parser.add_argument("-l", "--file_location",
        action="store", default="/tmp/cf_results.txt",
        help="the location you want the raw output stored default: /tmp/cf_results.txt")
   parser.add_argument("-f", "--uri_file_location",
        action="store", default="/tmp/cf_new_uri_results.txt",
        help="the location you want the output for new uri's stored default: /tmp/cf_new_uri_results.txt")
   parser.add_argument("-q", "--uri_db_location",
        action="store", default="/tmp/capture.db",
        help="the location you want the db for new uri's stored default: /tmp/capture.db")
   parser.add_argument("-s", "--server_list",
        action="store", default="single",
        help="type of query to user single or all  default: single")
   parser.add_argument("-d", "--per_page",
        action="store", default=50,
        help="results per page")
   parser.add_argument("-t", "--start_date",
        action="store", default="01/07/2019T00:00",
        help="This is how far to go back by start date default:01/07/2019T00:00")
   parser.add_argument("-e", "--email_sender",
        action="store", default="sender@sending.domain.com",
        help="Who you want the sender to look like")
   parser.add_argument("-g", "--email_rcpt",
        action="store", default="rcpt@recieving.domain.com",
        help="Who you would like to have the emails sent to")
   parser.add_argument("-j", "--email_forwarder",
        action="store", default="127.0.0.1",
        help="Server used as forwarder")
   
   
   args = parser.parse_args()
  
   if not args.username:
      parser.error('missing username')
   if not args.token:
      parser.print_help()
      parser.error('missing token')
 
   if args.server_list == 'single':
      single_query(args)
      send_mail(args)

if __name__ == '__main__':
   main()
