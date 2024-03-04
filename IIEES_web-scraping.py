#!/usr/bin/env python

#@autohr:A.Komeazi

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium
from time import sleep
import wget
from selenium.webdriver.common.by import By

######
def write_table_of_phases(table, filename):
    txt = table.get_attribute('outerHTML')
    #txt = '<table>' + table.get_attribute('outerHTML') + '</table>'
    #txt = table.text
    replace = [('IIEES SC', 'IIEES_SC'),
               ('Phase Type', 'Phase_Type'),
               ('Phase Quality', 'Phase_Quality'),
               ('First Motion ', 'First_Motion'),
               ('Observed Arrival Time', 'Observed_Arrival_Date Observed_Arrival_Time'),
               ('Time Residual', 'Time_Residual'),
               ('Loc. Flag', 'Loc_Flag'),
               ('Input Weight ', 'Input_Weight'),
               (' ', ',')]
    #for re in replace:
    #    txt = txt.replace(*re)
    with open(filename, 'w') as outfile:
        outfile.write(txt)

def write_table_of_detail(table, filename):
    txt = table.text
    with open(filename, 'w') as outfile:
        outfile.write(txt)
###### search parameters#
start_year="2000/01/01"
start_time=""

end_year="2006/01/01"
end_time=""

min_lat="24"
max_lat="44"
min_lon="44"
max_lon="65"

min_dep=""
max_dep=""

min_mag="4.5"
max_mag=""


output_dir = '.'
######

### 1402-08-16 #
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
options = Options()
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
geckodriver_path = "/snap/bin/geckodriver"  # specify the path to your geckodriver
driver_service = Service(executable_path=geckodriver_path)
###

driver = webdriver.Firefox(options=options, service=driver_service)
driver.get("http://www.iiees.ac.ir/fa/eqcatalog/")

elem_1 = driver.find_element(By.NAME, "txtDate1")
elem_4 = driver.find_element(By.NAME, "txtHour1")
elem_5 = driver.find_element(By.NAME, "txtDate2")
elem_8 = driver.find_element(By.NAME, "txtHour2")
elem_9 = driver.find_element(By.NAME, "txtLat1")
elem_10 = driver.find_element(By.NAME, "txtLat2")
elem_11 = driver.find_element(By.NAME, "txtLon1")
elem_12 = driver.find_element(By.NAME, "txtLon2")
elem_13 = driver.find_element(By.NAME, "txtDepth1")
elem_14 = driver.find_element(By.NAME, "txtDepth2")
elem_15 = driver.find_element(By.NAME, "txtM1")
elem_16 = driver.find_element(By.NAME, "txtM2")
elem_17 = driver.find_element(By.NAME, "btnSubmit")


elem_1.clear()
elem_4.clear()
elem_5.clear()
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
elem_4.send_keys(start_time)
elem_5.send_keys(end_year)
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
# sleep(10)
#table = driver.find_element_by_xpath("//div/center/center/table/tbody")

myData = [element for element in driver.find_elements(By.XPATH,"//div/div/div/div/main/div/div/table/tbody/tr/td/a[contains(@href,'http://www.iiees.ac.ir/fa/eventspec?eqid')]")]
links = [elem.get_attribute('href') for elem in myData]

total_num = len(links)
for num, link in enumerate(links):
    print(num+1, 'of', total_num)
    try:
        _id = link.split('=')[-1]
        driver.get(link)
        # sleep(10)
        ### Waveform
        elem_dn=driver.find_element(By.XPATH, '//div/div/div/div/main/div/div/p/a[contains(@href,"http://www.iiees.ac.ir/fa/?iieesop")]')
        dn_links=elem_dn.get_attribute('href')
        print(dn_links)
        wget.download(dn_links,f"{output_dir}/")
        ### Phases
        table_phases = driver.find_element(By.ID, 'dgPhase')
        write_table_of_phases(table=table_phases,
                              filename=f'{output_dir}/Phases-{_id}.html')
        ### Details
        table_detail = driver.find_element(By.CLASS_NAME, 'ResultTable')
        write_table_of_detail(table=table_detail,
                              filename=f'{output_dir}/detail-{_id}.txt')
    except Exception as error:
        print("NO WAVE", error)
    

driver.close()
