#!/usr/bin/python
#
# This assumes that the input file will be a CSV, with a header line, and the columns in the following ordering:
#       ver,mode,workers,cores,osName,osVersion,osArch,jvmVendor,jvmVersion,jvmArch,jvmHeapMem,jvmOffHeapMem,fpset,queue,toolbox,id,ts
#
# This assumes that there is a running MySQL installation on localhost, its connection details in the below constants, with a schema
#       populated with the creation SQL script peer to this file on the filesystem.
#

import sys
if len(sys.argv) != 2:
    print("Usage: ./populate_stats_db.py path_to_csv_file.csv")
    exit()

DB_USER = "AAAAA"
DB_PASSWORD = "BBBBB"
DB_DATABASE = "CCCCC"

INSTALLATION_INSERT = "INSERT INTO installation (unique_id) VALUES (%s)"
INSTALLATION_ID_FETCH = "SELECT id FROM installation WHERE unique_id = %s"
EXECUTION_INSERT = ("INSERT INTO execution_description "
                        "(installation_id, execution_timestamp, toolbox_launched, queue_type, "
                        "fp_set_type, off_heap_memory, heap_memory, jvm_architecture, jvm_version, "
                        "jvm_vendor, os_architecture, os_version, os_name, core_count, worker_count, "
                        "mode, version) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

import csv
import datetime
import mysql.connector
from mysql.connector import errorcode

try:
	cnx = mysql.connector.connect(user=DB_USER, password=DB_PASSWORD, database=DB_DATABASE)
except mysql.connector.Error as err:
	if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
		print("Something is wrong with your user name or password")
	elif err.errno == errorcode.ER_BAD_DB_ERROR:
		print("Database does not exist")
	else:
		print(err)

cursor = cnx.cursor()

print("Connected to " + DB_DATABASE + " on localhost; will import data from " + sys.argv[1])

with open(sys.argv[1], 'rb') as csvfile:
    csvreader = csv.reader(csvfile)
    line_number = 1
    for csvrow in csvreader:
        if line_number > 1:
            unique_id_from_csv_row = csvrow[15]

            try:
                cursor.execute(INSTALLATION_INSERT, (unique_id_from_csv_row,))
            except mysql.connector.Error as err:
                if err.errno != errorcode.ER_DUP_ENTRY:
                    print(err)
                    continue

            cursor.execute(INSTALLATION_ID_FETCH, (unique_id_from_csv_row,))
            row = cursor.fetchone()
            if row is not None:
                id_to_use = row[0]
                timestamp = datetime.datetime.fromtimestamp(float(csvrow[16])/1000.0)
                toolbox_launched = csvrow[14] == "true"
                queue_type = csvrow[13]
                fp_set_type = csvrow[12]

                if (queue_type is not None) and (len(queue_type) == 0):
                    queue_type = None

                if (fp_set_type is not None) and (len(fp_set_type) == 0):
                    fp_set_type = None

                try:
                    cursor.execute(EXECUTION_INSERT, (id_to_use, timestamp, toolbox_launched, queue_type, fp_set_type, int(csvrow[11]), int(csvrow[10]), csvrow[9], csvrow[8], csvrow[7], csvrow[6], csvrow[5], csvrow[4], int(csvrow[3]), int(csvrow[2]), csvrow[1], csvrow[0]))

                    if (line_number % 100) == 0:
                        sys.stdout.write('. ')
                        sys.stdout.flush()
                except mysql.connector.Error as err: 
                    print("Problem attempting to insert CSV row number " + str(line_number) + ". Error message: " + str(err))
            else:
                print("Could not get installation id for " + unique_id_from_csv_row)

        line_number += 1
    print

cnx.commit()

cursor.close()
cnx.close()
