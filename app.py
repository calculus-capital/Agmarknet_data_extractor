import json
import logging
from selenium import webdriver
import configparser
import pandas as pd
from datetime import datetime, date, timedelta
import sys
import os

from modules.db import db_connect, fetch_status, add_data_to_db
from modules.extractor import extract



def dateRange(start_date, end_date):
    for n in range(int((end_date - start_date).days)+1):
        yield start_date + timedelta(n)

def saveAgMarknetData(driver, md_db, collectionName, collectionValidate, commodity, currentDate):
    logging.info("Checking fetch status for Date : {}".format(currentDate))
    status = fetch_status(md_db, collectionValidate, currentDate, commodity)
    logging.info("Fetch Status for Date : {} :: {}".format(currentDate, status))
    if status:
        logging.info('Data for specified Date already in DataBase')
    else:
        logging.info('Data Not Present in DB, Start Extraction for Date : {}'.format(currentDate))
        df = extract(driver, commodity, currentDate)
        logging.info ('Length of Final DF : {}'.format(len(df)))
        logging.info (df.head(3))
        price_records = df.to_dict('records')
        query = add_data_to_db(md_db, collectionName, price_records)
        if query == "Done":
            logging.info('Values Inserted for Commodity : {} :: Date : {}'.format(commodity, currentDate))

def initLogs():
    cwd = os.getcwd()
    logPath = cwd+'/logs'
    if os.path.isdir(logPath) == False:
        print ('logs Folder not present')
        os.mkdir(logPath)
    else :
        print ('logs Folder present')
    currentTimeStamp = datetime.now()
    logFileName = 'logs/logger_' + currentTimeStamp.strftime('%Y_%h_%d_%H_%M') + '.log';
    logging.basicConfig(filename=logFileName, level=logging.INFO, format='%(asctime)s : %(levelname)s : %(message)s')
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout)) 

def main():
    initLogs()
    config = configparser.ConfigParser()
    PATH = "C:\Program Files (x86)\chromedriver.exe"
    driver = webdriver.Chrome(PATH)
    try :
        config.read('config.ini')
        dbLink = config['DB']['dbLink']
        dbName = config['DB']['dbName']

        commodity = input("Enter the commodity: ").capitalize()
        print ('Commodity : {}'.format(commodity))
        collectionName = config['Collections'][commodity]
        collectionValidate = config['Collections'][commodity+'_validate']

        fromDateStr = input('Enter From Date (dd-mm-yyyy): ')
        toDateStr = input('Enter To Date (Inclusive) (dd-mm-yyyy):')
        md_db = db_connect(dbLink, dbName)

        fromDate = datetime.strptime(fromDateStr, '%d-%m-%Y').date()
        toDate = datetime.strptime(toDateStr, '%d-%m-%Y').date()

        for singleDate in dateRange(fromDate, toDate):
            currentDate = datetime.strftime(singleDate, '%d-%b-%Y')
            logging.info ('Current Date : {}'.format(currentDate))
            saveAgMarknetData(driver, md_db, collectionName, collectionValidate, commodity, currentDate)
    except Exception as error:
        logging.exception('Exception Thrown in Main App.py')
    finally:
        driver.quit()

if __name__ == '__main__':
    main()