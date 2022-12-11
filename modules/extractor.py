import json
import time
import sys
import pandas as pd

# from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import logging
from datetime import datetime

log = logging.getLogger(__name__)

PAGE_LINK = "https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity={}&Tx_State=0&Tx_District=0&Tx_Market=0&DateFrom={}&DateTo={}&Fr_Date={}&To_Date={}&Tx_Trend=0&Tx_CommodityHead={}&Tx_StateHead=--Select--&Tx_DistrictHead=--Select--&Tx_MarketHead=--Select--"

COL_RENAME_DICT = {
    "Min Price (Rs./Quintal)": "min_price",
    "Max Price (Rs./Quintal)": "max_price",
    "Modal Price (Rs./Quintal)": "modal_price",
    "District Name": "district",
    "Market Name": "market",
    "Commodity": "commodity",
    "Variety": "variety",
    "Grade": "grade",
    "Price Date": "price_date",
}


def extractFromSecondPage(driver, pageNumber):
    log.info("Extracting Page : {}".format(pageNumber))
    df_current = pd.DataFrame()
    try:
        nextElemPath = "/html/body/form/div[3]/div[6]/div[6]/div[1]/div[2]/div[3]/div/table/tbody/tr[52]/td/table/tbody/tr/td[1]/input"

        if driver.find_element_by_xpath(nextElemPath):
            driver.find_element_by_xpath(nextElemPath).click()
            time.sleep(10)
            html = driver.page_source
            df_current = pd.read_html(html)
            df_current = pd.DataFrame(df_current[3])

            nextElemPath = "/html/body/form/div[3]/div[6]/div[6]/div[1]/div[2]/div[3]/div/table/tbody/tr[52]/td/table/tbody/tr/td[3]/input"
            next = driver.find_element_by_xpath(nextElemPath)
            while next:
                next.click()
                time.sleep(10)
                html_next = driver.page_source
                df_next = pd.read_html(html_next)
                df_next = pd.DataFrame(df_next[3])
                df_current = df_current.append(df_next, ignore_index=True)
                next = driver.find_element_by_xpath(nextElemPath)
    except Exception as error:
        # log.exception("Exception during page : {} :: {}".format(pageNumber, error))
        pass
    finally:
        return df_current


def extract(driver, commodity_name, commodity_number, from_date, to_date):
    pageNumber = 1
    df = pd.DataFrame()

    url = PAGE_LINK.format(commodity_number, from_date, to_date, from_date, to_date, commodity_name)
    driver.get(url)
    # time.sleep(100)
    html = driver.page_source
    df_current = pd.read_html(html)
    df_current = pd.DataFrame(df_current[3])

    df_next = extractFromSecondPage(driver, pageNumber + 1)
    df = df_current.append(df_next, ignore_index=True)
    df.drop(columns=["Sl no."], inplace=True)
    df.dropna(inplace=True)
    df.rename(columns=COL_RENAME_DICT, inplace=True)
    df["price_date"] = df["price_date"].apply(lambda x: datetime.strptime(x, "%d %b %Y"))

    return df
