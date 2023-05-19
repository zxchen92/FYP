import logging
import pandas as pd
import re

foodlist_raw = pd.read_csv('foodtest.csv')
foodlist = foodlist_raw.drop(columns=['foodCategory', 'categoryName', 'dietary_restrictions', 'location'])

food_name = foodlist['foodName'].str.replace(' ', '+')

foodlist["placeURL"] = ("https://www.google.com/maps/search/" + food_name + "+in+singapore")
foodlist["foodid"] = foodlist["id"]

dfFoodlist = foodlist[["foodid", "placeURL"]]
dfPlaceURL = pd.read_csv('place_url.csv')

dfDiff = dfFoodlist[ ~dfFoodlist.foodid.isin(dfPlaceURL.foodid)].dropna()
# print(dfFoodlist)
# print(dfPlaceURL)

dfDiff.to_csv(r'place_urltest.csv', columns=['foodid', 'placeURL'], mode='a', index=False, header=False)

