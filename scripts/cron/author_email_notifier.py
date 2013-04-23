#!/usr/bin/env python

#default_date = 1 week
output_file = "/tmp/email_notifier.dat"

from datetime import datetime, timedelta, tzinfo
import shutil
import os, os.path
import sys
import getopt

from trac.env import Environment
from multiproject.core.db import admin_query, admin_transaction, safe_int
from trac.notification import NotifyEmail
from multiproject.core.configuration import conf
from multiproject.common.notifications.email import EmailNotifier
from trac.notification import NotificationSystem

def usage():
    print "Usage: %s -i <interval or number of weeks e.g -i 1 >" % (os.path.basename(sys.argv[0]))
    print
    print "Emails authors of local account about their expiry in the time frame given"
    sys.exit(3)

def error_exit(message="Unknown error", exitcode=1):
    message = "Error: %s" % message
    print message
    try:
        f=open(output_file, "w")
        f.write("code=%d\n" % exitcode)
        f.write("msg=%s\n" % message)
        f.close()
    except IOError:
        print "Error writing output file"
    sys.exit(exitcode)

def get_args():
    try:
        opts, _ = getopt.getopt(sys.argv[1:], "hi:", ["help"])
    except getopt.GetoptError:
        usage()
    interval = None

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o == '-i':
            try:
                interval = int(a)
            except ValueError:
                 print "Invalid value for -i"
                 usage()

    if not interval:
        print "interval missing"
        usage()
    return interval


def admin_queri(author_id):

   query_author = """ SELECT givenName, lastName, mail 
                  FROM user
                  WHERE user_id = %s
                  """
   with admin_query() as cursor:
        try:
           cursor.execute(query_author, author_id)
           for row in cursor:
               return row
        except Exception as e:
               error_exit(e)


def send_mail(message, receiver):
         env = Environment(conf.getEnvironmentSysPath(conf.sys_home_project_name))
         notifier = NotificationSystem(env)
         from_email = env.config['notification'].get('smtp_from')
         replyto_email = env.config['notification'].get('smtp_replyto')
         sender = from_email or replyto_email

         try: 
            notifier.send_email(sender, receiver, message)
         except Exception as e:
            error_exit(e)
         return True

def admin_msg(admin, user):
    adm_msg = "Hi "+admin[0]+" "+admin[1]+ "\n\n\n"
    adm_msg += "Your authored account with username "+user[1]+" will expire on %s" % user[5]
    adm_msg +="\n\n" 

    return adm_msg


def user_msg(admin, user):
    msg = "Hi "+user[2]+" "+user[3]+ "\n\n\n"
    msg += "Your account with username "+user[1]+" will expire on %s" % user[5]
    msg += "\n\nPlease take contact with your account author "+admin[0]+" "+admin[1]+" email: "+admin[2]+" to extend it if needed."
    msg +="\n\n" 

    return msg

if __name__ == '__main__':
   interval = get_args()

   #get all user account that will expire in 1 week
   q = """ 
       SELECT author_id, username, givenName, lastName, mail, expires FROM user 
       WHERE expires BETWEEN NOW() AND DATE_SUB(NOW(), INTERVAL %s WEEK)
       AND author_id IS NOT NULL
       ORDER BY author_id ASC 
       """ % interval
   


   with admin_query() as cursor:
       try:
          cursor.execute(q)
          for user in cursor:
              admin =  admin_queri(user[0])
              adm_msg = admin_msg(admin, user)
              send_mail(adm_msg, admin[2])
              user_mssg = user_msg(admin, user)
              send_mail(user_mssg, user[4])
       except Exception as e:
              error_exit(e)

