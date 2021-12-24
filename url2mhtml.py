#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 20 09:24:45 2021

@author: shalo
"""
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor

import re, os
import hashlib
import xlrd
import openpyxl
import time


def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    mstr = r"[\'“”\s']"
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    new_title = re.sub(mstr, "", title) #删除特殊字符
    return new_title


def get_profile():
    chromeOptions = webdriver.ChromeOptions()
    chromeOptions.add_argument('--headless')  # 谷歌无头模式
    chromeOptions.add_argument('--disable-gpu')  # 禁用显卡
    chromeOptions.add_argument('window-size=1280,800')  # 指定浏览器分辨率
    chromeOptions.add_argument("--no-sandbox")
    return chromeOptions


def get_browser():
    #with webdriver.Chrome(ChromeDriverManager().install()) as browser:
    #    return browser
    browser = webdriver.Chrome(options=get_profile())
    return browser

def _get_page(initial_url,save_path):
    print(initial_url)
    browser = get_browser()
    browser.get(initial_url)
    time.sleep(5)

    html = browser.page_source
    if title := re.search("<title>(.*?)</title>", html, flags=re.S):
        title = title.group(1)
    if title != "404错误_C语言中文网" and title:
        title = validateTitle(title)
        # 执行 Chome 开发工具命令，得到mhtml内容
        res = browser.execute_cdp_cmd('Page.captureSnapshot', {})
        #html = browser.execute_cdp_cmd('return document.documentElement.outerHTML', {})
        #print(html)

        
        #求文件MD5
        myhash = hashlib.md5()
        myhash.update(html.encode("utf8"))
        pageMD5 = myhash.hexdigest()
        print(pageMD5)
        
        #存储为mhtml
        print(title)
        get_time = time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
        filename = os.path.join(save_path, '{}.mhtml'.format(title+get_time))
        print(filename)
        with open(filename, 'w', newline='') as f:
            f.write(res['data'])
        
    browser.close()
    
def snapshot_page(url_file,result_path):
    input_xlsx= openpyxl.load_workbook(url_file)
    #sheet_names=input_xlsx.get_sheet_names()
    ws = input_xlsx[r"输入"]
    
    # 获取sheet的最大行数和列数
    rows = ws.max_row
    cols = ws.max_column
    #for r in range(1,rows):
    #    for c in range(1,cols):
    #        print(ws.cell(r,c).value)
    #    if r==10:
    #            break
            
    #sheet = readbook.sheet_by_index(0)
    #nrows = sheet.nrows#行
    #ncols = sheet.ncols#列
    print(rows)
    for i in range(1,rows):             
        web = ws.cell(i+1,1).value #网站名称
        Section = ws.cell(i+1,2).value #板块名称
        url = ws.cell(i+1,3).value   #url地址
        getdate = time.strftime("%Y-%m-%d", time.localtime()) #当前日期
        
        #创建首级目录-网站
        newpath = os.path.join(result_path,web)        
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        
        #以板块创建子目录
        newpath = os.path.join(newpath,Section)        
        if not os.path.exists(newpath):
            os.makedirs(newpath)
            
        #以当前日期创建子目录
        newpath = os.path.join(newpath,getdate) 
        if not os.path.exists(newpath):
            os.makedirs(newpath)
            
        #print(newpath)
        _get_page(url,newpath)
        #time.sleep(5)
        
        #print("sss")
        #print(url)
        #_get_page(url,save_path)
        #result_path=os.path.join(result_path,table.cell(1,i).value)
        #if os.path.exists(os.path.join(result_path,table.cell(1,i).value)):            
        #else:
        #    os.makedirs(os.path.join(result_path,table.cell(1,i).value))

if __name__ == '__main__':
    page_url = f"https://qiita.com/mochi_yu2/items/e2480ae3b2a6db9d7a98"
    save_path = r"/home/shalo/downloadMhtml"
    url_file = r"./config/urls.xlsx"
    
    snapshot_page(url_file,save_path)
    #os.path.exists(save_path)
    #_get_page(page_url,save_path)