# -*- coding: utf-8 -*-
import logging

Logger = logging.getLogger("TBTrackerSpider")
Logger.setLevel(logging.DEBUG)
InfoHandler = logging.FileHandler("TBTracker_Log/spider_info.log")
InfoHandler.setLevel(logging.INFO)
INFOFORMATTER = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s]: %(message)s')
InfoHandler.setFormatter(INFOFORMATTER)
Logger.addHandler(InfoHandler)
ErrHandler = logging.FileHandler("TBTracker_Log/spider_error.log")
ErrHandler.setLevel(logging.ERROR)
ERRORFORMATTER = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] File "%(filename)s", line %(lineno)d: %(message)s')
ErrHandler.setFormatter(ERRORFORMATTER)
Logger.addHandler(ErrHandler)

import requests
import smtplib
import sqlite3 as sqlite
import xlwt

from email import encoders
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.utils import parseaddr, formataddr

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from TBTracker_AuxiliaryFunction import get_current_system_time, get_current_system_date

HEADERS = {
    'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0',
}

def find_out_real_price(shop_url):
    price, taobao_price = '', ''
    try:
        driver = webdriver.PhantomJS()
        driver.set_window_size(800, 400)
        driver.get(shop_url)
        tm_price_panel = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'J_StrPriceModBox')))
        price = WebDriverWait(tm_price_panel, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'tb-rmb-num'))).text.strip()
        try:
            tm_promo_panel = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'J_PromoPrice')))
            taobao_price = WebDriverWait(tm_promo_panel, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'tb-rmb-num'))).text.strip()
        except Exception as e:
            taobao_price = '无'
    except Exception as e:
        price = WebDriverWait(tm_price_panel, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'tm-price'))).text.strip()
        try:
            tm_promo_panel = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'J_PromoPrice')))
            taobao_price = WebDriverWait(tm_promo_panel, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'tm-price'))).text.strip()
        except Exception as e:
            taobao_price = '无'
    finally:
        driver.close()
    return (price, taobao_price)

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

def main():
    conn = sqlite.connect('TBTracker_DB/TBTracker.db')
    c = conn.cursor()

    c.execute('select URL from product')
    URLList = [query[0] for query in c.fetchall()]
    c.execute('select Price from product')
    priceList = [query[0] for query in c.fetchall()]
    c.execute('select TaobaoPrice from product')
    taobaoPriceList = [query[0] for query in c.fetchall()]
    Logger.info('总共有{}件商品的数据需要跟踪...'.format(len(URLList)))
    changeCNT = 0
    emmitList = []
    for i, url in enumerate(URLList):
        res = find_out_real_price(url)
        Logger.info('第{}件商品的数据跟踪成功...'.format(i + 1))
        deltaPrice = 0.0
        deltaTaoBaoPrice = 0.0
        currentTime = get_current_system_time()
        if priceList[i] != res[0]:
            Logger.info('第{}件商品的价格数据发生改变'.format(i + 1))
            c.execute('update product set Price="{}", CreateTime="{}" where URL="{}"'.format(res[0], currentTime, url))
            conn.commit()
            deltaPrice = res[0] - priceList[i]
        else:
            Logger.info('第{}件商品的价格数据未发生改变'.format(i + 1))
        if taobaoPriceList[i] != res[1]:
            Logger.info('第{}件商品的淘宝价格数据发生改变'.format(i + 1))
            c.execute('update product set TaoBaoPrice="{}", CreateTime="{}" where URL="{}"'.format(res[1], currentTime, url))
            conn.commit()
            deltaTaoBaoPrice = res[1] - taobaoPriceList[i]
        else:
            Logger.info('第{}件商品的淘宝价格数据未发生改变'.format(i + 1))
        if deltaPrice != 0.0 or deltaTaoBaoPrice != 0.0:
            changeCNT += 1
            emmitList.append((i, deltaPrice, deltaTaoBaoPrice))
    Logger.info('商品数据跟踪完毕！')

    if changeCNT != 0:
        c.execute('select * from product')
        queries = c.fetchall()

        excel = xlwt.Workbook()
        sheet = excel.add_sheet('淘宝商品数据', cell_overwrite_ok=True)

        pattern1 = xlwt.Pattern()
        pattern1.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern1.pattern_fore_colour = 3
        style1 = xlwt.XFStyle()
        style1.pattern = pattern1

        pattern2 = xlwt.Pattern()
        pattern2.pattern = xlwt.Pattern.SOLID_PATTERN
        pattern2.pattern_fore_colour = 2
        style2 = xlwt.XFStyle()
        style2.pattern = pattern2

        sheet.write(0, 0, "商品标识")
        sheet.write(0, 1, "URL")
        sheet.write(0, 2, "标题")
        sheet.write(0, 3, "店铺名")
        sheet.write(0, 4, "价格")
        sheet.write(0, 5, "变更值")
        sheet.write(0, 6, "淘宝价")
        sheet.write(0, 7, "变更值")
        sheet.write(0, 8, "上次更新时间")
        for i in range(changeCNT):
            sheet.write(i + 1, 0, queries[emmitList[i][0]][0])
            sheet.write(i + 1, 1, queries[emmitList[i][0]][1])
            sheet.write(i + 1, 2, queries[emmitList[i][0]][2])
            sheet.write(i + 1, 3, queries[emmitList[i][0]][3])
            sheet.write(i + 1, 4, queries[emmitList[i][0]][4])
            if emmitList[i][1] > 0.0:
                sheet.write(i + 1, 5, emmitList[i][1], style1)
            elif emmitList[i][1] < 0.0:
                sheet.write(i + 1, 5, emmitList[i][1], style2)
            elif emmitList[i][1] == 0.0:
                sheet.write(i + 1, 5, '-')
            sheet.write(i + 1, 6, queries[emmitList[i][0]][5])
            if emmitList[i][2] > 0.0:
                sheet.write(i + 1, 7, emmitList[i][2], style1)
            elif emmitList[i][2] < 0.0:
                sheet.write(i + 1, 7, emmitList[i][2], style2)
            elif emmitList[i][2] == 0.0:
                sheet.write(i + 1, 7, '-')
            sheet.write(i + 1, 8, queries[emmitList[i][0]][6])
        excel.save('TBTracker_Excel/{}-淘宝商品数据变更表.xlsx'.format(get_current_system_date()))

        msg = MIMEMultipart('alternative')
        msg['From'] = _format_addr('TBTracker机器人<summychou@163.com>')
        msg['To'] = _format_addr('管理员<825942030@qq.com>')
        msg['Subject'] = Header('TBTracker机器人发送的邮件', 'utf-8').encode()
        msg.attach(MIMEText('Life is Short, I Use Python!', 
            'plain', 'utf-8'))
        msg.attach(MIMEText('<html><body> \
            <p><img src="cid:1"></p> \
            <h3>Life is Short, I Use Python!</h3> \
            </body></html>', 
            'html', 'utf-8'))

        with open('TBTracker_Excel/{}-淘宝商品数据变更表.xlsx'.format(get_current_system_date()), 'rb') as f:
            mimeExcel = MIMEBase('excel', 'xlsx', filename=Header('{}-淘宝商品数据变更表.xlsx'.format(get_current_system_date()), 'utf-8').encode())
            mimeExcel.add_header('Content-Disposition', 'attachment', filename=Header('{}-淘宝商品数据变更表.xlsx'.format(get_current_system_date()), 'utf-8').encode())
            mimeExcel.add_header('Content-ID', '<0>')
            mimeExcel.add_header('X-Attachment-Id', '0')
            mimeExcel.set_payload(f.read())
            encoders.encode_base64(mimeExcel)
            msg.attach(mimeExcel)

        with open('TBTracker_Excel/python.png', 'rb') as f:
            mimeImage = MIMEBase('image', 'png', filename='python.png')
            mimeImage.add_header('Content-Disposition', 'attachment', filename='python.png')
            mimeImage.add_header('Content-ID', '<1>')
            mimeImage.add_header('X-Attachment-Id', '1')
            mimeImage.set_payload(f.read())
            encoders.encode_base64(mimeImage)
            msg.attach(mimeImage)

        smtp = smtplib.SMTP('smtp.163.com', '25')
        smtp.login('summychou@163.com', 'yunan0808')
        smtp.sendmail('summychou@163.com', ['825942030@qq.com'], msg.as_string())
        smtp.quit()

    c.close()

if __name__ == '__main__':
    main()
