#!/usr/bin/env python3

import cv2
import os
import sys
import datetime
import sqlite3
import time
import pyautogui
from pyzbar.pyzbar import decode
from PIL import Image
from threading import Thread

stop = False

def record_log(did, un, act):
    path = "./log/" + did + ".csv"
    f = open(path, 'a')
    log = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S") + "," + un + "," + act + "\n"
    f.write(log)
    f.close()

def user_search(id):
    con = sqlite3.connect("user.db")
    cur = con.cursor()
    cur.execute('select * from ut where user_id=?;', (int(id),))
    ret = cur.fetchone();
    con.close()
    return ret

def borrow_device(did, un):
    record_log(did, un, "貸出")
    con = sqlite3.connect("manage_device.db")
    cur = con.cursor()
    cur.execute('UPDATE mdt SET user_name=? where device_name=?;', (un, did))
    cur.execute('UPDATE mdt SET device_status=? where device_name=?;', ("貸出中", did))
    cur.execute('UPDATE mdt SET last_modify_date=? where device_name=?;', (datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), did))
    con.commit()
    con.close()
    return 0

def device_search(did):
    con = sqlite3.connect("manage_device.db")
    cur = con.cursor()
    cur.execute('select * from mdt where device_name=?;', (did,))
    ret = cur.fetchone();
    con.close()
    return ret

def return_device(did, un):
    record_log(did, un, "返却")
    con = sqlite3.connect("manage_device.db")
    cur = con.cursor()
    cur.execute('UPDATE mdt SET user_name=? where device_name=?;', ('-', did))
    cur.execute('UPDATE mdt SET device_status=? where device_name=?;', ('貸出可', did))
    cur.execute('UPDATE mdt SET last_modify_date=? where device_name=?;', (datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), did))
    con.commit()
    con.close()
    return 0

def timer(secs):
    print("Lock")
    f = open('lock', 'a')
    f.close()
    for i in range(secs, -1, -1):
        time.sleep(1)
    os.remove('lock')
    print("Unlock")

def lock_unlock():
    target_time = 5
    thread = Thread(target=timer,args=(target_time,))
    thread.start()

def login_user(user_name):
    if user_name == "admin":
        f = open('admin', 'w')
        f.write(user_name)
        f.close()
    f = open('login_user', 'w')
    f.write(user_name)
    f.close()

def logout_user(user_name):
    if user_name == "admin":
        os.remove('admin')
    os.remove('login_user')

def timer_log(secs):
    i = secs
    while not stop:
        if i == 0:
            break
        print(i)
        i -= 1
        time.sleep(1)
    if not stop:
        f = open('timeup', 'w')
        f.write('timeup')
        f.close()

def auto_log(target_time):
    thread = Thread(target=timer_log,args=(target_time,))
    thread.start()

def compare_log():
    cpos = str(pyautogui.position())
    f = open('logger', 'r')
    for line in f:
        if(line == cpos):
            f.close()
            return True
    f.close()
    return False

def delf():
    if os.path.exists('logger'):
        os.remove('logger')
    if os.path.exists('timeup'):
        os.remove('timeup')

def modify_log(msg):
    f = open('logger', 'w')
    f.write(msg)
    f.close()

if __name__ == "__main__":
    capture = cv2.VideoCapture(0)
    if capture.isOpened() is False:
        raise("IO Error")
    flag = 0
    lf = 0
    userid = 0
    username = ""

    while True:
        ret, frame = capture.read()
        if ret == False:
            continue

        cv2.imshow("frame", frame)
        data = decode(frame)

        if not os.path.exists('lock'):
            if data != []:
                code = data[0][0].decode('utf-8', 'ignore')
                cols = code.split(":")
    
                # Login / Logout
                if cols[0] == "userid":
                    if username == "":
                        rec = user_search(cols[1])
                        if rec != None:
                            userid = cols[1]
                            username = rec[2]
                            lf = 1
                            print("Hi! {0}!! Please show device_id which you want to borrow or return.".format(rec[2]))
                            login_user(username)
                            lock_unlock()
                        else:
                            print("Your UserID is not found. Please ask your administrator.")
                    else:
                        print("Good Bye! {0}!!".format(username))
                        logout_user(username)
                        stop = True
                        delf()
                        userid = 0
                        username = ""
                        lf = 0
                        lock_unlock()

                # Return / Borrow
                if cols[0] == "deviceid":
                    if lf == 1:
                        rec = device_search(cols[1])
                        if rec != None:
                            if rec[3] == "-":
                                borrow_device(cols[1], username)
                                print("{0} borrowed {1} machine.".format(username, cols[1]))
                                modify_log("borrow")
                                lock_unlock()
                            else:
                                return_device(cols[1], username)
                                print("{0} is returned. Thank you:)".format(cols[1]))
                                modify_log("return")
                                lock_unlock()
                        else:
                            print("This DeviceID is not found. Please ask your administrator.")
                    else:
                        print("Please show your user_id if you want to borrow or return.")

            # auto_logout
            if os.path.exists('login_user'):
                if not os.path.exists('logger'):
                    f = open('logger', 'w')
                    f.write(str(pyautogui.position()))
                    f.close()
                    stop = False
                    auto_log(60)
                if os.path.exists('timeup'):
                    if compare_log():
                        print("auto logout is done")
                        delf()
                        print("Good Bye! {0}!!".format(username))
                        logout_user(username)
                        userid = 0
                        username = ""
                        lf = 0
                    else:
                        print("interrupt auto logout")
                        os.remove('timeup')
                        f = open('logger', 'w')
                        f.write(str(pyautogui.position()))
                        f.close()
                        stop = False
                        auto_log(10)

        k = cv2.waitKey(1)
        if k == 27:
            break

    capture.release()
    cv2.destroyAllWindows()
        
