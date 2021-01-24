# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 21:06:21 2020

@author: sleep
"""
#%% Part 3 - Extractor
def cleaner(page):
    #scale down the problem
    html = str(page) 
    begin = html.find('\\n<tr class="table-row" style="cursor: pointer;"')
    end = html.find("</small></td>\\n</tr> </tbody>\\n", begin)
    rawpagereduced = (html[begin:end])
    #Split the string up into rows
    df = rawpagereduced.split("/td>\\n</tr>")
    #remove the tip 
    for element in df:
        if element.find("TIPS!") != -1:
            df.remove(element)
    return df
def splitter(df):
    #split the strings into columns
    seperator = ";"
    index = 0
    for element in df:
        element = element.replace('\\n<tr class="table-row" style="cursor: pointer;" data-href="', '')
        element = element.replace('">\\n', seperator)
        element = element.replace('</small></b><br />', seperator)
        element = element.replace('\\n', seperator)
        element = element.replace(';">', seperator)
        element = element.replace('</b><br /><small>', seperator)
        element = element.replace('</small><', '')
        df[index] = element
        index +=1
    import pandas as pd
    df = pd.DataFrame(df)
    df.columns = ["Name"]
    df = df["Name"].str.split(';', expand = True)
    from datetime import date
    df.columns = ["Wadress", "Name", "Adress", "Colour", "Price", "Date Entered"]
    df['Date Collected'] = date.today()
    return df
def misc(df):
    #can remove the ugly parts, such as <small> and make the letters swedish (å ä ö)
    df = df.replace(to_replace = ['<td>', '<b>', '<small>', '</td>', '<b style="color:'], value = '', regex = True)
    df['Price'] = df['Price'].replace('kr', '', regex = True)
    df = df.replace('\xc3\xa5','å', regex = True)
    return df

#%% Scraper of each individual page
#load in a text file with the latest date that the webpage was scraped
from datetime import date
import os
import pandas as pd
try: #check laptop
    os.chdir( 'Insert the path to your folder here' )
except FileNotFoundError:
    print('do desktop')
versionfile = open("lastchecked.txt", "r")
versiondate = versionfile.read()   
date = str(date.today())
if versiondate == date: #if this is true then scraping has been done today and the script shuts down
    proceed = False
    versionfile.close()
else: #this it isn't true then it continues, setting proceed to True and updating the version file
    proceed = True
    versiondate = versiondate.replace(versiondate,date)
    versionfile = open("lastchecked.txt", "w")
    versionfile.write(versiondate)
    versionfile.close()
#if proceed is true, then there hasn't been any webscraping today and the script continues

iteration = 1
while proceed:
    try:
        base = "https://bensinpriser.nu/stationer/95/alla/alla/"
        number = str(iteration)
        webpage = base + number
        from urllib.request import Request, urlopen
        req = Request(webpage, headers={'User-Agent': 'Mozilla/5.0'})
        page = urlopen(req).read()
        df = cleaner(page)
        df = splitter(df)
        df = misc(df)
        iteration
        try: 
            df_big = df_big.append(df)
        except NameError:
            df_big = pd.DataFrame()
            df_big = df_big.append(df)
        iteration = iteration + 1
    except ValueError:
        break
if proceed:
    import pandas as pd
    from openpyxl import load_workbook
    df = df_big
    writer = pd.ExcelWriter('Scraped.xlsx', engine='openpyxl')
    writer.book = load_workbook('Scraped.xlsx')
    writer.sheets = dict((ws.title, ws) for ws in writer.book.worksheets)
    reader = pd.read_excel(r'Scraped.xlsx')
    df.to_excel(writer,index=False,header=False,startrow=len(reader)+1)
    writer.close()

if proceed:
    if iteration ==1:
        print(iteration, 'page was scraped')
    else:
        print(iteration, 'pages were scraped')
    import time
    time.sleep(2.5)
