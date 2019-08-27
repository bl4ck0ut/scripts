#!/usr/bin/python
#: Title       : Cofense Triage API
#: Date Created: Mon Aug 26 2019
#: Author      : Charley Pfaff
#: Description : API used to query Cofense to file
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
# What this does is:
# 1.logs into Cofense Triage
# 2.performs a defined search
# 3.returns results to a text file
# 4. delay of 15 seconds between requests to account for Triage request throttling
# -----------------------------------------------------------------------
#
# improvments
# - add time and date range as variable
# - add fields to be reported 
# - read initial rquest and parge last page as loop variable
#
# --------------------------------------------------------------
# ChangeLog
# - Located in git history
# --------------------------------------------------------------


from triagelib import TriageSession
import json
import time, sys
import argparse

def single_query(args):
   triage = TriageSession(host=args.host_name, email=args.username, apikey=args.token)

   f = open(args.file_location, 'w')
   count=1
   reports = "placeholder"
   while reports and count < 40:
      reports = triage.inbox_reports(start_date=args.start_date, per_page=args.per_page, page=(count))
      time.sleep(15)
      for x in reports:
         cof_urls = x['email_urls']
         for y in cof_urls:
            ct_url = y['url']
            rep_url = x['reported_at']
            rep_sub = x['report_subject']
            f.write(rep_url.encode('utf-8') + ' , ' + rep_sub.encode('utf-8').replace("," , "") + ' , ' + ct_url.encode('utf-8') + '\n')
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
        help="the location you want the output stored default: /tmp/cf_results.txt")
   parser.add_argument("-s", "--server_list",
        action="store", default="single",
        help="type of query to user single or all  default: single")
   parser.add_argument("-d", "--per_page",
        action="store", default=50,
        help="results per page")
   parser.add_argument("-t", "--start_date",
        action="store", default="01/07/2019T00:00",
        help="This is how far to go back by start date default:01/07/2019T00:00")
   args = parser.parse_args()
  
   if not args.username:
      parser.error('missing username')
   if not args.token:
      parser.print_help()
      parser.error('missing token')
 
   if args.server_list == 'single':
      single_query(args)

if __name__ == '__main__':
   main()
