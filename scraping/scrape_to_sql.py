from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
import pandas as pd
import os
import re
from unidecode import unidecode

no_cred = "NO CREDIT"
re_eval = "RE-EVALUATION REQUIRED"
under_rev = "UNDER REVIEW"
no_options = "No transfer credits"

provinces = ["Manitoba", "Alberta", "British Columbia", "New Brunswick", "Newfoundland and Labrador", "Nova Scotia", "Nunavut", "Ontario", "Quebec", "Prince Edward Island", "Saskatchewan"]

url = "https://aurora.umanitoba.ca/ssb/ksstransequiv.p_trans_eq_main?rpt_type=current"

sql_filename = "entries.sql"

# Headless browser options
options = webdriver.FirefoxOptions()
options.add_argument('--headless')


# Delete old SQL file if exists
if os.path.exists(sql_filename):
    os.remove(sql_filename)

# Intialise driver
driver = webdriver.Firefox(service=FirefoxService(executable_path=GeckoDriverManager().install()), options=options)
driver.get(url)


# Start at the beginning of sql file
open(sql_filename, "w").close()
sql_writer = open(sql_filename, "a")
sql_writer.write("--Dropping table\n")
sql_writer.write("DROP TABLE IF EXISTS Entry;\n\n")
sql_writer.write("--Table Creation\n\n")
sql_writer.write("CREATE TABLE Entry(id INTEGER PRIMARY KEY, province TEXT, university_name TEXT, course_details TEXT, uofm_course_details TEXT, comments TEXT, effective_date TEXT);\n\n")
sql_writer.write("--Inserts\n")

for curr_province in provinces:

    # Click on current province
    select_province = Select(driver.find_element(By.XPATH, '/html/body/div[4]/table[1]/tbody/tr[2]/td[1]/form/select'))
    select_province.select_by_visible_text(curr_province)

    # Click on each university in curr_province
    select_uni = Select(driver.find_element(By.XPATH, '/html/body/div[4]/table[1]/tbody/tr[2]/td[2]/form/select'))
    university_list = [option.text for option in select_uni.options]

    for uni_option in university_list:
        curr_university = uni_option
        select_uni = Select(driver.find_element(By.XPATH, '/html/body/div[4]/table[1]/tbody/tr[2]/td[2]/form/select'))
        select_uni.select_by_visible_text(curr_university)

        # Click on each faculty
        select_faculty = Select(driver.find_element(By.XPATH, '/html/body/div[4]/table[1]/tbody/tr[2]/td[3]/form/select'))
        faculty_list = [option.text for option in select_faculty.options]

        for faculty_option in faculty_list:

            curr_faculty = faculty_option
            select_faculty = Select(driver.find_element(By.XPATH, '/html/body/div[4]/table[1]/tbody/tr[2]/td[3]/form/select'))
            

            if("Unknown" not in curr_faculty):
                select_faculty.select_by_visible_text(curr_faculty)

                # Now scrape generated table 
                try:
                    final_table = WebDriverWait(driver, 1).until( 
                        EC.presence_of_element_located((By.XPATH, "/html/body/div[4]/table[2]"))
                )
                    curr_dataframe = pd.read_html(final_table.get_attribute('outerHTML'))[0]
                except TimeoutError:
                    print("Timeout error")

                curr_dataframe.columns = curr_dataframe.columns.droplevel()

                # Iterate over scraped table
                for index, row in curr_dataframe.iterrows():
                    #clean up strings
                    adj_row_0 = re.sub("'", "''", row[0])
                    adj_row_0 = re.sub('"', '', adj_row_0)
                    adj_row_0 = unidecode(adj_row_0)

                    adj_row_1 = re.sub("'", "''", row[1])
                    adj_row_1 = re.sub('"', '', adj_row_1)
                    adj_row_1 = unidecode(adj_row_1)

                    adj_row_2 = ""
                    if(not pd.isna(row[2])):
                        adj_row_2 = re.sub("'", "''", row[2])
                        adj_row_2 = re.sub('"', '', adj_row_2)
                        adj_row_2 = unidecode(adj_row_2) 
  
                    adj_curr_prov = re.sub("'", "''", curr_province)
                    adj_curr_prov = re.sub('"', '', adj_curr_prov)
                    adj_curr_uni = re.sub("'", "''", curr_university)
                    adj_curr_uni = re.sub('"', '', adj_curr_uni)  
                    adj_curr_uni = unidecode(adj_curr_uni)                  
                                                

                    # only include approved courses
                    if(no_cred not in row[1] and re_eval not in row[1] and under_rev not in row[1] and no_options not in row[1]):
   
                        if(pd.isna(row[2])):
                            values = "'" + adj_curr_prov + "', '" + adj_curr_uni + "', '" + adj_row_0 + "', '" + adj_row_1 + "', " + " '' " + ", '" + row[3] + "'"
                        else:
                            #clean up quotes
                            adj_row_2 = re.sub("'", "''", row[2])
                            adj_row_2 = re.sub('"', '', adj_row_2)   

                            values = "'" + adj_curr_prov + "', '" + adj_curr_uni + "', '" + adj_row_0 + "', '" + adj_row_1 + "', '" + adj_row_2 + "', '" + row[3] + "'"
                        insert_statement = "INSERT INTO Entry(province, university_name, course_details, uofm_course_details, comments, effective_date) VALUES(" + values + ");\n"
                        sql_writer.write(insert_statement)
driver.quit()
sql_writer.close()
quit()







        


    

