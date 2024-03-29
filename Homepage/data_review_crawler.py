from django.http import HttpResponse
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import time
import pandas as pd

def data_review_crawler():
    chrome_driver_path = 'chromedriver.exe'


    chrome_options = Options()
    driver = webdriver.Chrome(executable_path=chrome_driver_path, options=chrome_options)

    foodID_list =[]
    userID_Rlist = []
    name_list = []
    stars_Rlist = []
    duration_list = []

    placeURL_list = (pd.read_csv("google_place.csv")['URL Link'])
    food_list = (pd.read_csv("google_place.csv")['Food ID'])
    foodPlace_dict = dict(zip(placeURL_list, food_list))

    for url, food in foodPlace_dict.items():
        driver.get(url)
        time.sleep(3)

        try:
            #click review tab
            driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]').click()
            time.sleep(1)
        except NoSuchElementException:
            print(f"Review tab not found for {url}")
            continue
        
        try:
            #click Sort button
            driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div[7]/div[2]/button').click()
            time.sleep(1)
        except NoSuchElementException:
            print(f"Review tab not found for {url}")
            continue

        try:
            #click sort by newest
            driver.find_element(By.XPATH, '//*[@id="action-menu"]/div[2]').click()
            time.sleep(2)
        except NoSuchElementException:
            print(f"Sort newest not found for {url}")
            continue

        SCROLL_PAUSE_TIME = 1

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

            ele = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]')

            new_height = driver.execute_script("return arguments[0].scrollHeight", ele)

            if number == 2:
                break

            if new_height == last_height:
                break

            print('cont')
            last_height = new_height

        item = driver.find_elements(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div[9]')

        time.sleep(3)

        for i in item:
            userID = i.find_elements(By.CLASS_NAME, "WEBjve")
            name = i.find_elements(By.CLASS_NAME, "d4r55")
            stars = i.find_elements(By.CLASS_NAME, "kvMYJc")
            duration = i.find_elements(By.CLASS_NAME, "rsqaWe")

            for j,k,l,p in zip(userID, name, stars, duration):
                foodID_list.append(food)
                userID_Rlist.append(j.get_attribute('data-href'))
                name_list.append(k.text)
                stars_Rlist.append(l.get_attribute("aria-label"))
                duration_list.append(p.text)

    #transform
    userID_list =re.findall(r'\d+', str(userID_Rlist))
    stars_list =re.findall(r'\d+', str(stars_Rlist))

    dfTwo = pd.DataFrame(list(zip(foodID_list,userID_list, name_list, stars_list, duration_list)),
                            columns=['Food ID','userID', 'name', 'rating', 'duration'])
    print(dfTwo)

    #delta load
    dfTwo.to_csv(r'UserID_v1.csv', columns=['userID','name'], mode='a', index=False, header=False)
    dfTwo.to_csv(r'FoodRatings_v1.csv', columns=['userID','Food ID','rating'], mode='a', index=False, header=False)

    messageComplete = "Completed!"
        
    return messageComplete



    