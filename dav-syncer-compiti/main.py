#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Programma che scarica i compiti da nuvola date le credenziali di un account, segnalando eventuali novità salvandole sotto forma di warning.
from json import loads, dumps
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from time import sleep
from datetime import datetime, timedelta

path = "/home/botwht/dav-syncer-compiti/"
usr = "alberto gilardino"
pwd = ""


def check_loaded_by_click(by_what, petrarca):
    try:
        WebDriverWait(driver, 2).until(expected_conditions.element_to_be_clickable((by_what, petrarca)))
    except:
        pass

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome("/usr/local/bin/chromedriver", options = chrome_options)
driver.get("https://nuvola.madisoft.it/login")
driver.find_element_by_xpath('//*[@id="username"]').send_keys(usr)
driver.find_element_by_xpath('//*[@id="password"]').send_keys(pwd + Keys.ENTER)
check_loaded_by_click(By.XPATH, '//a[@href="/area-studente/compiti"]')

with open(path+"compiti.json", "r") as openfile:
    try:
        data = openfile.read()
        compiti = loads(data)
    except:
        print("UDDIO! Cannot load JSON file compiti.json")
        quit()
with open(path+"warning.json", "r") as openfile:
    try:
        data = openfile.read()
        warning = loads(data)
    except:
        print("UDDIO! Cannot load JSON file warning.json")
        quit()


num_days = 15
current_date = datetime.now()
for n in range(num_days):
    new_date = current_date + timedelta(n-1)
    date = new_date.strftime("%Y-%m-%d")
    driver.get("https://nuvola.madisoft.it/area-studente/compiti?data="+ date +"&vista=giorno")
    check_loaded_by_click(By.XPATH, '//*[@id="app"]/div/main/div/div[2]/div/ul/li[1]/strong')
    compito = []
    count = 1
    found = False
    while True:
        try:
            compito = []
            compito.append(driver.find_element_by_xpath('//*[@id="app"]/div/main/div/div[2]/div/ul/li[' + str(count) + ']/span').text.replace("\n", "").strip().upper())
            compito.append(driver.find_element_by_xpath('//*[@id="app"]/div/main/div/div[2]/div/ul/li[' + str(count) + ']/h2').text.replace("\n", "").strip().upper())
            compito.append(driver.find_element_by_xpath('//*[@id="app"]/div/main/div/div[2]/div/ul/li[' + str(count) + ']/div/a').text.replace("\n", "").strip()) 
            compito.append(driver.find_element_by_xpath('/html/body/div/div/main/div/div[2]/div/ul/li[' + str(count) + ']/div/small[1]').text.replace("\n", "").strip()) 
            compito.append(driver.find_element_by_xpath('//*[@id="app"]/div/main/div/div[2]/div/ul/li[' + str(count) + ']/div/ul/li/p').text.replace("\n", "").strip())
            try:
                compito.append(driver.find_element_by_xpath('//*[@id="app"]/div/main/div/div[2]/div/ul/li[' + str(count) + ']/div/ul/li/div/ul[2]/li').text.replace("\n", "").strip())
            except:
                compito.append("")
            compito.append(count)
            compito.append(date)
            for i in range(len(compiti)):
                if compiti[i][1] == compito[1] and compiti[i][3] == compito[3] and compiti[i][-1] == compito[-1]:
                    if not(compiti[i][2] == compito[2] and compiti[i][4] == compito[4]) and compiti[i][-2] == compito[-2]:
                        warning.append([date, compito, compiti[i], str(datetime.now().hour) + ":" + ("0" if datetime.now().minute<10 else "") + str(datetime.now().minute) + " e " + ("0" if datetime.now().second<10 else "") + str(datetime.now().second) + " secondi", False])
                    compiti[i] = compito
                    found = True
            if not found:
                warning.append([date, compito, ("0" if datetime.now().hour<10 else "") + str(datetime.now().hour) + ":" + ("0" if datetime.now().minute<10 else "") + str(datetime.now().minute) + " e " + ("0" if datetime.now().second<10 else "") + str(datetime.now().second) + " secondi", True])
                compiti.append(compito)
            else:
                found = False
            count += 1
        except: #Exception as e:
            break

json_compiti = dumps(compiti, indent = 4)
json_warning = dumps(warning, indent = 4)

with open(path+"warning.json", "w") as outfile:
    outfile.write(json_warning)
with open(path+"compiti.json", "w") as outfile:
    outfile.write(json_compiti)

driver.quit()
