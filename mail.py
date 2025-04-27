# -*- coding: utf-8 -*- 

import os
import re
import csv
import mimetypes
from optparse import OptionParser
import smtplib
from email.message import EmailMessage

email_re = r"\A[a-zA-Z0-9!#$%&'*+/=?^_‘{|}~-]+(?:\.[a-zA-Z0-9!#$%&'*+/=?^_‘{|}~-]+)*@(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\.)+[a-zA-Z0-9](?:[a-zA-Z0-9-]*[a-zA-Z0-9])?\Z"
def send(host,port,user,password,subject,from_name,to_addr, msg,from_addr):
    srv = smtplib.SMTP(host, port)
    srv.ehlo()
    srv.starttls()
    srv.login(user, password)
    em = EmailMessage()
    em.set_content(msg)
    em["Subject"] = subject
    em["From"] = f"{from_name} <{from_addr}>"
    em["To"] = to_addr
    if not re.fullmatch(email_re, to_addr):
        print(f"Wrong email: {to_addr}")
    else:
        try:
            srv.send_message(em)
        except Exception as e:
            
            print(f"Error: {to_addr}")
        else:
            print(f"Sent: {to_addr}")
