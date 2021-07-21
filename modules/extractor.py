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

PAGE_LINK='https://agmarknet.gov.in/SearchCmmMkt.aspx?Tx_Commodity={}&Tx_State=0&Tx_District=0&Tx_Market=0&DateFrom={}&DateTo={}&Fr_Date={}&To_Date={}&Tx_Trend=0&Tx_CommodityHead={}&Tx_StateHead=--Select--&Tx_DistrictHead=--Select--&Tx_MarketHead=--Select--'

COL_RENAME_DICT = {'Min Price (Rs./Quintal)':'min_price', 'Max Price (Rs./Quintal)':'max_price', 'Modal Price (Rs./Quintal)':'modal_price', 'District Name':'district', 'Market Name':'market', 'Commodity':'commodity', 'Variety':'variety', 'Grade':'grade', 'Price Date':'price_date'}

def commodity_validate(commodity):
    com = False
    comm_num = 0
    comm_name = ''
    with open('data.json', 'r') as j:
        commodities = json.loads(j.read())
    for comm_no in commodities:
        if commodity.lower() == commodities[comm_no].lower():
            com = True
            comm_num = comm_no
            comm_name = commodities[comm_no]
    return com, comm_num, comm_name


# Function for the next page after 2 pages
def next_to_second(driver, pageNumber):
    logging.info("Extracting Page : {}".format(pageNumber))
    nextElemPath = '//*[@id="cphBody_GridPriceData"]/tbody/tr[52]/td/table/tbody/tr/td[3]/input'
    df = pd.DataFrame()
    try:
        if driver.find_element_by_xpath(nextElemPath):
            driver.find_element_by_xpath(nextElemPath).click()
            time.sleep(10)
            html_next = driver.page_source
            df_current = pd.read_html(html_next)
            df_current = pd.DataFrame(df_current[3])
            logging.info('Data Extracted Process is done for page : {} :: DF Length: {}'.format(pageNumber, len(df_current)))
            df_next = next_to_second(driver, pageNumber+1)
            df = df_current.append(df_next, ignore_index=True)
    except Exception as error:
        logging.exception ('Exception during page : {} :: {}'.format(pageNumber, error))
    finally:
        return df


def extractFromSecondPage(driver, pageNumber):
    logging.info("Extracting Page : {}".format(pageNumber))
    df = pd.DataFrame()
    try:
        nextElemPath = '//*[@id="cphBody_GridPriceData"]/tbody/tr[52]/td/table/tbody/tr/td[1]/input'
        if driver.find_element_by_xpath(nextElemPath):
            driver.find_element_by_xpath(nextElemPath).click()
            time.sleep(10)
            html = driver.page_source
            df_current = pd.read_html(html)
            df_current = pd.DataFrame(df_current[3])
            logging.info('Data Extracted Process is done for page : {} :: DF Length: {}'.format(pageNumber, len(df_current)))
            df_next = next_to_second(driver, pageNumber+1)
            df = df_current.append(df_next, ignore_index=True)
    except Exception as error:
        logging.exception ('Exception during page : {} :: {}'.format(pageNumber, error))
    finally:
        return df


def extract(driver, commodity, date):
    logging.info("Start Validation : {} :: {}".format(commodity, date))
    validation, commodity_number, comm_name = commodity_validate(commodity)
    logging.info ("Validation Status : {}".format(validation))
    pageNumber = 1
    df = pd.DataFrame()
    if validation:
        url = PAGE_LINK.format(commodity_number, date, date, date, date, comm_name)
        driver.get(url)
        time.sleep(10)
        html = driver.page_source
        df_current = pd.read_html(html)
        df_current = pd.DataFrame(df_current[3])
        logging.info('Data Extracted Process is done for page : {} :: DF Length: {}'.format(pageNumber, len(df_current)))
        df_next = extractFromSecondPage(driver, pageNumber+1);
        df = df_current.append(df_next, ignore_index=True)
        df.drop(columns=['Sl no.'], inplace=True)
        df.dropna(inplace=True)
        df.rename(columns=COL_RENAME_DICT, inplace=True)
        df['price_date'] = df['price_date'].apply(lambda x: datetime.strptime(x, '%d %b %Y'))
    else:
        logging.error("Entered commodity not found! Please Try again....")
    return df

        
