import json
import logging
from selenium import webdriver
import configparser
import pandas as pd
from datetime import datetime, date, timedelta
import sys
import os

from modules.extractor import extract
from modules.commodities import commodities

log = logging.getLogger(__name__)


def dateRange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


def saveAgMarknetData(driver, commodity_name, commodity_number, from_date, to_date):
    df = extract(driver, commodity_name, commodity_number, from_date, to_date)
    log.info("Length of Final DF : {}".format(len(df)))
    df.to_csv(f"{commodity_number}.csv")


def main():
    config = configparser.ConfigParser()
    driver = webdriver.Firefox()

    for commodity in commodities:
        try:
            print("Commodity : {}".format(commodity))

            fromDateStr = "01-01-2010"
            toDateStr = "11-12-2022"

            fromDate = datetime.strptime(fromDateStr, "%d-%m-%Y").date()
            toDate = datetime.strptime(toDateStr, "%d-%m-%Y").date()

            fromDate = datetime.strftime(fromDate, "%d-%b-%Y")
            toDate = datetime.strftime(toDate, "%d-%b-%Y")
            saveAgMarknetData(driver, commodity["name"], commodity["value"], fromDate, toDate)
        except Exception as error:
            logging.exception("Exception Thrown in Main App.py")

    driver.quit()


if __name__ == "__main__":
    main()
