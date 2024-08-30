#!/usr/bin/env python

#@autohr:A.Komeazi
# selenium.__version__
# Out[28]: '4.7.2'

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium
from time import sleep
import wget
import os
from selenium.webdriver.common.by import By

###### create a folder to save the data in
os.system("mkdir -p ./downloaded_data")
###### search parameters#
# for start_month in range(1, 13):
# start_month = str(start_month).zfill(2)
start_year="2020"
start_month="01"
start_day="01"
start_time="00"

end_year="2023"
end_month="01"
end_day="15"
end_time="00"

min_lat="24"
max_lat="44"
min_lon="44"
max_lon="65"

min_dep="0"
max_dep=""

min_mag="4.5"
max_mag=""
######

driver = webdriver.Firefox()
driver.get("http://irsc.ut.ac.ir/bulletin.php?lang=fa")

elem_1 = driver.find_element(By.NAME, "start_Y")
elem_2 = driver.find_element(By.NAME, "start_M")
elem_3 = driver.find_element(By.NAME, "start_D")
elem_4 = driver.find_element(By.NAME, "start_H")
elem_5 = driver.find_element(By.NAME, "end_Y")
elem_6 = driver.find_element(By.NAME, "end_M")
elem_7 = driver.find_element(By.NAME, "end_D")
elem_8 = driver.find_element(By.NAME, "end_H")
elem_9 = driver.find_element(By.NAME, "min_lat")
elem_10 = driver.find_element(By.NAME, "max_lat")
elem_11 = driver.find_element(By.NAME, "min_lon")
elem_12 = driver.find_element(By.NAME, "max_lon")
elem_13 = driver.find_element(By.NAME, "min_dep")
elem_14 = driver.find_element(By.NAME, "max_dep")
elem_15 = driver.find_element(By.NAME, "min_mag")
elem_16 = driver.find_element(By.NAME, "max_mag")
elem_17 = driver.find_element(By.NAME, "action")


elem_1.clear()
elem_2.clear()
elem_3.clear()
elem_4.clear()
elem_5.clear()
elem_6.clear()
elem_7.clear()
elem_8.clear()
elem_9.clear()
elem_10.clear()
elem_11.clear()
elem_12.clear()
elem_13.clear()
elem_14.clear()
elem_15.clear()
elem_16.clear()

elem_1.send_keys(start_year)
elem_2.send_keys(start_month)
elem_3.send_keys(start_day)
elem_4.send_keys(start_time)
elem_5.send_keys(end_year)
elem_6.send_keys(end_month)
elem_7.send_keys(end_day)
elem_8.send_keys(end_time)
elem_9.send_keys(min_lat)
elem_10.send_keys(max_lat)
elem_11.send_keys(min_lon)
elem_12.send_keys(max_lon)
elem_13.send_keys(min_dep)
elem_14.send_keys(max_dep)
elem_15.send_keys(min_mag)
elem_16.send_keys(max_mag)


elem_17.click()
# table = driver.find_elements(By.XPATH, "//div/center/center/table/tbody/tr/td/a[text() = 'Wave file']")
table = driver.find_elements(By.XPATH, "//div/center//center/table/tbody/tr/td/a[text() = 'Wave file']")
myData = [element for element in table]
links = [elem.get_attribute('href') for elem in myData]


for link in links:
    try:
        
        driver.get(link)
        elem_dn=driver.find_element(By.XPATH, '//a[contains(@href,"/tm/")]')
        dn_links=elem_dn.get_attribute('href')
        wget.download(dn_links,"./downloaded_data/")
    except:
        print("NO WAVE")
driver.close()
