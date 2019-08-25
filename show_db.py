#!/usr/bin/env python3

import sqlite3
import signal
import time
import datetime


con = sqlite3.connect("manage_device.db")
cur = con.cursor()
sql = 'select * from mdt;'

def task(arg1, arg2):
    print("*********************************")
    print(datetime.datetime.now())
    print("#,device_name,device_status,user_name,last_modify_date")
    for row in cur.execute(sql):
        print(row)

signal.signal(signal.SIGALRM, task)
signal.setitimer(signal.ITIMER_REAL, 0.1, 3.0)

while True:
    time.sleep(1)


con.close()
