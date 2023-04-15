from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import re
import time
from bs4 import BeautifulSoup
from misc import save_as_pickle
from tqdm import tqdm
import logging
import pandas as pd

chrome_driver_path = r"\chromedriver.exe"

options = webdriver.ChromeOptions()
driver = webdriver.Chrome(executable_path=chrome_driver_path, options=options)

url = 'https://www.google.com/maps/place/Swee+Choon+Tim+Sum+Restaurant/@1.3081642,103.8569394,17z/data=!4m8!3m7!1s0x31da19c804e450bf:0x1dbecd26daa7df7e!8m2!3d1.3081642!4d103.8569394!9m1!1b1!16s%2Fg%2F1thxy9qp'

driver.get(url)
time.sleep(5)

driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div[7]/div[2]/button').click()

time.sleep(1)

driver.find_element(By.XPATH, '//*[@id="action-menu"]/div[2]').click()

time.sleep(5)

SCROLL_PAUSE_TIME = 6

# Get scroll height
last_height = driver.execute_script("return document.body.scrollHeight")

number = 0

while True:
    number = number + 1

    # Scroll down to bottom

    ele = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]')

    driver.execute_script('arguments[0].scrollBy(0, 8000);', ele)

    # Wait to load page

    time.sleep(SCROLL_PAUSE_TIME)

    # Calculate new scroll height and compare with last scroll height
    print(f'last height: {last_height}')

    ele = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]')

    new_height = driver.execute_script("return arguments[0].scrollHeight", ele)

    print(f'new height: {new_height}')

    if number == 5:
        break

    if new_height == last_height:
        break

    print('cont')
    last_height = new_height

item = driver.find_elements(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div[9]')

time.sleep(3)

userID_Rlist = []
name_list = []
stars_Rlist = []
duration_list = []

for i in item:

    button = i.find_elements(By.TAG_NAME, 'button')
    for m in button:
        if m.text == "More":
            m.click()
    time.sleep(5)

    userID = i.find_elements(By.CLASS_NAME, "WEBjve")
    name = i.find_elements(By.CLASS_NAME, "d4r55")
    stars = i.find_elements(By.CLASS_NAME, "kvMYJc")
    duration = i.find_elements(By.CLASS_NAME, "rsqaWe")

    for j,k,l,p in zip(userID, name, stars, duration):
        userID_Rlist.append(j.get_attribute('href'))
        name_list.append(k.text)
        stars_Rlist.append(l.get_attribute("aria-label"))
        duration_list.append(p.text)

#transform
userID_list =re.findall(r'\d+', str(userID_Rlist))
stars_list =re.findall(r'\d+', str(stars_Rlist))

review = pd.DataFrame(
    {'userID': userID_list,
     'name': name_list,
     'rating': stars_list,
     'duration': duration_list})

review.to_excel(r'C:\Users\cheng\google_review.xlsx',index=False)
print(review)