#!/usr/bin/env python3

import sqlite3

con = sqlite3.connect("manage_device.db")
cur = con.cursor()
cur.execute("create table mdt(id integer primary key autoincrement, device_name varchar(255) not null, device_status varchar(255) not null, user_name varchar(255) not null, last_modify_date varchar(255) not null);")
device = [('123','','-',''), ('456','','-',''), ('789','','-','')]
cur.executemany("insert into mdt(device_name,device_status,user_name,last_modify_date) values(?,?,?,?);", device)
con.commit();
sql = 'select * from mdt;'
for row in cur.execute(sql):
    print(row)
con.close()

con = sqlite3.connect("user.db")
cur = con.cursor()
cur.execute("create table ut(id integer primary key autoincrement, user_id integer, name varchar(255) not null);")
user = [(1,'ichiro'),(2,'ziro'),(3,'saburo')]
cur.executemany("insert into ut(user_id, name) values (?,?);", user)
con.commit();
sql = 'select * from ut;'
for row in cur.execute(sql):
    print(row)
con.close()

