# -*- coding: utf-8 -*-
# ********************第三方相关模块导入********************
import logging

Logger = logging.getLogger("TBTracker")
Logger.setLevel(logging.DEBUG)
InfoHandler = logging.FileHandler("TBTracker_Log/info.log")
InfoHandler.setLevel(logging.INFO)
INFOFORMATTER = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s]: %(message)s')
InfoHandler.setFormatter(INFOFORMATTER)
Logger.addHandler(InfoHandler)
ErrHandler = logging.FileHandler("TBTracker_Log/error.log")
ErrHandler.setLevel(logging.ERROR)
ERRORFORMATTER = logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] File "%(filename)s", line %(lineno)d: %(message)s')
ErrHandler.setFormatter(ERRORFORMATTER)
Logger.addHandler(ErrHandler)

import math
import matplotlib.dates as mdate
import matplotlib.pyplot as plt
import os
import random
import requests
import sqlite3 as sqlite
import sys
import xlwt
import yaml

from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from wordcloud import WordCloud
# ********************PyQt5相关模块导入********************
from PyQt5.QtCore import QEvent
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import qApp
from PyQt5.QtWidgets import QAbstractItemView
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QFrame
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QHeaderView
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QRadioButton
from PyQt5.QtWidgets import QSlider
from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtWidgets import QTreeWidget
from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtWidgets import QTreeWidgetItemIterator
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QWidget
# ********************用户自定义相关模块导入********************
from TBTracker_AuxiliaryFunction import *
from TBTracker_Gui.TBTracker_Gui_Button import *
from TBTracker_Gui.TBTracker_Gui_Canvas import *
from TBTracker_Gui.TBTracker_Gui_Dialog import *

'''
@author  : Zhou Jian
@email   : zhoujian@hust.edu.cn
@version : V1.0
@date    : 2017.01.24
'''

class TBTrackerMainWindow(QWidget):
    def __init__(self):
        super(TBTrackerMainWindow, self).__init__()
        self.create_main_window()

    def create_main_window(self):
        self.setWindowTitle("淘宝商品数据跟踪系统")
        self.setWindowIcon(QIcon('TBTracker_Ui/python.png'))
        self.width, self.height = get_current_screen_size()
        self.setMinimumSize(self.width, self.height)
        self.setMaximumSize(self.width, self.height)
        self.set_widgets()
        self.setLayout(self.layout)

        self.show_database()
        self.plot_word_cloud()
        self.plot_product_tree()

    def set_widgets(self):
        q_1_Font = QFont()
        q_1_Font.setPointSize(16)

        labelFont = QFont()
        labelFont.setPointSize(12)

        q_2_Font = QFont()
        q_2_Font.setPointSize(12)

        self.table_1_Font = QFont()
        self.table_1_Font.setPointSize(10)
        self.table_1_Font.setStyleName("Bold") 
        self.table_2_Font = QFont()
        self.table_2_Font.setPointSize(12)
        self.table_2_Font.setStyleName("Bold")

        self.headers = {'user-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:50.0) Gecko/20100101 Firefox/50.0'}

        # ****************************************
        firstWidget = QWidget()

        taobaoLabel = QLabel()
        logImage = QImage("TBTracker_Ui/tb_log.webp").scaled(int(148 * 0.8), int(66 * 0.8))
        taobaoLabel.setPixmap(QPixmap.fromImage(logImage))
        self.searchLineEdit = QLineEdit()
        self.searchLineEdit.setFont(q_1_Font)
        searchButton = SearchButton()
        searchButton.setFont(q_1_Font)
        searchButton.clicked.connect(self.call_spider)

        searchRegionLayout = QHBoxLayout()
        searchRegionLayout.setContentsMargins(240, 0, 240, 0)
        searchRegionLayout.setSpacing(20)
        searchRegionLayout.addWidget(taobaoLabel)
        searchRegionLayout.addWidget(self.searchLineEdit)
        searchRegionLayout.addWidget(searchButton)
        
        self.taobaoDataTable = QTableWidget(0, 4)
        self.taobaoDataTable.horizontalHeader().hide()
        self.taobaoDataTable.verticalHeader().hide()
        self.taobaoDataTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.taobaoDataTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.progressBar = QProgressBar()
        
        self.productIDLineEdit = QLineEdit()
        self.productIDLineEdit.setFont(q_2_Font)
        productIDSaveButton = SaveButton()
        productIDSaveButton.setFont(q_2_Font)
        productIDSaveButton.clicked.connect(self.save_product_id)
        updateDataButton = UpdateButton()
        updateDataButton.setFont(q_2_Font)
        updateDataButton.clicked.connect(self.update_data)

        dataOperateLayout = QHBoxLayout()
        dataOperateLayout.setContentsMargins(500, 0, 0, 0)
        dataOperateLayout.addStretch()
        dataOperateLayout.setSpacing(20)
        dataOperateLayout.addWidget(self.productIDLineEdit)
        dataOperateLayout.addWidget(productIDSaveButton)
        dataOperateLayout.addWidget(updateDataButton)

        firstWidgetLayout = QVBoxLayout()
        firstWidgetLayout.setSpacing(10)
        firstWidgetLayout.addLayout(searchRegionLayout)
        firstWidgetLayout.addWidget(self.taobaoDataTable)
        firstWidgetLayout.addWidget(self.progressBar)
        firstWidgetLayout.addLayout(dataOperateLayout)

        firstWidget.setLayout(firstWidgetLayout)
        # ****************************************

        # ****************************************
        secondWidget = QWidget()
        self.DBTable = QTableWidget(0, 6)
        self.DBTable.setHorizontalHeaderLabels(["商品标识", "标题", "店铺名", "价格", "淘宝价", "是否删除数据？"])
        self.DBTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.DBTable.setSelectionMode(QAbstractItemView.NoSelection)
        self.DBTable.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.addButton = AddButton()
        self.addButton.clicked.connect(self.add_data)
        deleteButton = DeleteButton()
        deleteButton.clicked.connect(self.delete_data)

        DBOperateLayout = QHBoxLayout()
        DBOperateLayout.addStretch()
        DBOperateLayout.setSpacing(20)
        DBOperateLayout.addWidget(self.addButton)
        DBOperateLayout.addWidget(deleteButton)

        secondWidgetLayout = QVBoxLayout()
        secondWidgetLayout.setSpacing(10)
        secondWidgetLayout.addWidget(self.DBTable)
        secondWidgetLayout.addLayout(DBOperateLayout)

        secondWidget.setLayout(secondWidgetLayout)
        # ****************************************

        # ****************************************
        thirdWidget = QWidget()
        
        self.wordCloudLabel = QLabel()
        self.wordCloudLabel.setAlignment(Qt.AlignCenter)
        self.wordCloudLabel.setFrameStyle(QFrame.Panel | QFrame.Plain)
        self.wordCloudLabel.setLineWidth(2)
        self.wordCloudLabel.setPixmap(QPixmap.fromImage(QImage("TBTracker_Ui/WordCloud.png")))

        self.productTree = QTreeWidget()
        self.productTree.setColumnCount(2)
        self.productTree.setHeaderLabels(['商品标识','商品数量'])
        self.productTree.header().setSectionResizeMode(QHeaderView.Stretch)
        self.productTree.setSelectionMode(QAbstractItemView.NoSelection)
        productTreeLayout = QHBoxLayout()
        productTreeLayout.addWidget(self.productTree)

        upLayout = QHBoxLayout()
        upLayout.setSpacing(20)
        upLayout.addWidget(self.wordCloudLabel)
        upLayout.addLayout(productTreeLayout)

        exportButton = ExportButton()
        exportButton.clicked.connect(self.export_data)
        allSelectButton = AllSelectButton()
        allSelectButton.clicked.connect(self.select_all)
        dataExportLayout = QHBoxLayout()
        dataExportLayout.addStretch()
        dataExportLayout.setSpacing(20)
        dataExportLayout.addWidget(allSelectButton)
        dataExportLayout.addWidget(exportButton)

        thirdWidgetLayout = QVBoxLayout()
        thirdWidgetLayout.setSpacing(20)
        thirdWidgetLayout.setContentsMargins(50, 20, 50, 20)
        thirdWidgetLayout.addLayout(upLayout)
        thirdWidgetLayout.addLayout(dataExportLayout)
        
        thirdWidget.setLayout(thirdWidgetLayout)
        # ****************************************

        # ****************************************
        fourthWidget = QWidget()

        self.historyDataCanvas = HistoryDataCanvas()
        historyDataLayout = QVBoxLayout()
        historyDataLayout.addWidget(self.historyDataCanvas)

        self.selectCommodityButton = SelectCommodityButton()
        self.monthlyDataButton = MonthlyDataButton()
        self.yearlyDataButton = YearlyDataButton()
        manualUpdateButton = ManualUpdateButton()
        manualUpdateButton.clicked.connect(self.manual_update)
        buttonLayout = QHBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.setSpacing(30)
        buttonLayout.addWidget(self.selectCommodityButton)
        buttonLayout.addWidget(self.monthlyDataButton)
        buttonLayout.addWidget(self.yearlyDataButton)
        buttonLayout.addWidget(manualUpdateButton)
        
        fourthWidgetLayout = QVBoxLayout()
        fourthWidgetLayout.setSpacing(10)
        fourthWidgetLayout.setContentsMargins(50, 0, 50, 10)
        fourthWidgetLayout.addLayout(historyDataLayout)
        fourthWidgetLayout.addLayout(buttonLayout)

        fourthWidget.setLayout(fourthWidgetLayout)
        # ****************************************

        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(firstWidget, "数据爬虫")
        self.tabWidget.addTab(secondWidget, "数据后台")
        self.tabWidget.addTab(thirdWidget, "数据导出")
        self.tabWidget.addTab(fourthWidget, "数据跟踪")

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 20, 50, 13)
        self.layout.addWidget(self.tabWidget)

    # 类方法重载 -- 关闭窗口事件
    def closeEvent(self, event):
        messageDialog = MessageDialog()
        reply = messageDialog.question(self, "消息提示对话框", "您要退出系统吗?", messageDialog.Yes | messageDialog.No, messageDialog.No)
        if reply == messageDialog.Yes:
            event.accept()
        else:
            event.ignore()
    
    @staticmethod
    def remove_pics():
        root_dir = 'TBTracker_Temp'
        for root, dirs, files in os.walk(root_dir):
            Logger.info('正在删除图片...')
            for filename in files:
                os.remove(root+'/'+filename)
            Logger.info('图片删除完毕!')

    def find_out_real_price(self, i, shop_url, match_price):
        title, price, taobao_price = "", "", ""
        try:
            html = requests.get(shop_url, timeout=10, headers=self.headers)
            Logger.info("第{0}家店铺的商品页面读取成功...".format(i))
            soup = BeautifulSoup(html.text, 'lxml')
            try:
                title = soup.find(name='h3', attrs={'class': 'tb-main-title'})['data-title'].strip()
            except Exception as e:
                try:
                    title = soup.find(name='div', attrs={'class': 'tb-detail-hd'}).find(name='h1').get_text().strip()
                except Exception as e:
                    title = soup.find(name='div', attrs={'class': 'main-box'}).find(name='h2').get_text().split("】")[1].split("（")[0].strip()
                    taobao_price = soup.find(name='div', attrs={'class': 'main-box'}).find(name='span', attrs={'class': 'J_actPrice'}).get_text().lstrip("￥").strip()
                    price = soup.find(name='div', attrs={'class': 'main-box'}).find(name='del', attrs={'class': 'originPrice'}).get_text().lstrip("￥").strip()
                    return title, price, taobao_price
            try:
                price = soup.find(name='li', attrs={'id': 'J_StrPriceModBox'}). \
                    find(name='em', attrs={'class': 'tb-rmb-num'}).get_text().strip()
                if match_price != price:
                    taobao_price = match_price
            except Exception as e:
                try:
                    driver = webdriver.PhantomJS()
                    driver.set_window_size(800, 400)
                    driver.get(shop_url)
                    tm_price_panel = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'tm-price-panel')))
                    price = WebDriverWait(tm_price_panel, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'tm-price'))).text.strip()
                    driver.close()
                    if match_price != price:
                        taobao_price = match_price
                except Exception as e:
                    try:
                        tm_promo_panel = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'tm-promo-panel')))
                        price = WebDriverWait(tm_promo_panel, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'tm-price'))).text.strip()
                        driver.close()
                        if match_price != price:
                            taobao_price = match_price
                    except Exception as e:
                        Logger.error(e)
        except Exception as e:
            Logger.error(e)
            Logger.warn('第{0}家店铺的商品页面读取失败...'.format(i))
        finally:
            if taobao_price == "":
                taobao_price = "无"
            return title, price, taobao_price

    def call_spider(self):
        searchWord = self.searchLineEdit.text().strip()
        if searchWord != "":
            self.remove_pics()
            try:
                webDriver = webdriver.PhantomJS()
                webDriver.set_window_size(800, 400)
                try:
                    Logger.info("模拟登录淘宝网")
                    webDriver.get("https://www.taobao.com/")
                    try:
                        search_combobox = WebDriverWait(webDriver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'search-combobox-input-wrap')))
                        search_input = WebDriverWait(search_combobox, 10).until(
                            EC.presence_of_element_located((By.ID, 'q')))
                        # 发送搜索词
                        search_input.send_keys(searchWord.strip())

                        search_button_wrap = WebDriverWait(webDriver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'search-button')))
                        search_button = WebDriverWait(search_button_wrap, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'btn-search')))
                        search_button.click()
                        try:
                            Logger.info('搜索成功，正在返回搜索结果...')
                            main_srp_item_list = WebDriverWait(webDriver, 10).until(
                                EC.presence_of_element_located((By.ID, 'mainsrp-itemlist')))
                            m_item_list = WebDriverWait(main_srp_item_list, 10).until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'm-itemlist')))
                            items = WebDriverWait(m_item_list, 10).until(
                                EC.presence_of_all_elements_located((By.CLASS_NAME, 'items')))[0]
                            allItems = WebDriverWait(items, 10).until(
                                EC.presence_of_all_elements_located((By.CLASS_NAME, 'J_MouserOnverReq'))
                            )
                            
                            self.returnCNT = len(allItems)
                            Logger.info('总共返回{0}个搜索结果'.format(self.returnCNT))

                            self.taobaoDataTable.clearContents()
                            self.taobaoDataTable.setRowCount(self.returnCNT * 6)

                            imageLabel = [QLabel() for _ in range(self.returnCNT)]
                            titleItem = [QTableWidgetItem() for _ in range(self.returnCNT)]
                            shopItem = [QTableWidgetItem("店铺：") for _ in range(self.returnCNT)]
                            shopValueItem = [QTableWidgetItem() for _ in range(self.returnCNT)]
                            sourceItem = [QTableWidgetItem("来源地：") for _ in range(self.returnCNT)]
                            sourceValueItem = [QTableWidgetItem() for _ in range(self.returnCNT)]
                            priceItem = [QTableWidgetItem("价格：") for _ in range(self.returnCNT)]
                            priceValueItem = [QTableWidgetItem() for _ in range(self.returnCNT)]
                            tbPriceItem = [QTableWidgetItem("淘宝价：") for _ in range(self.returnCNT)]
                            tbPriceValueItem = [QTableWidgetItem() for _ in range(self.returnCNT)]
                            dealItem = [QTableWidgetItem("付款人数：") for _ in range(self.returnCNT)]
                            dealValueItem = [QTableWidgetItem() for _ in range(self.returnCNT)]
                            isJoinedItem = [QTableWidgetItem("是否加入价格跟踪队列？") for _ in range(self.returnCNT)]
                            checkItem = [QTableWidgetItem() for _ in range(self.returnCNT)]
                            self.URLList = []

                            # 抓取商品图
                            for (j, item) in enumerate(allItems):
                                try:
                                    Logger.info('正在爬取第{0}家店铺的数据...'.format(j + 1))
                                    itemPic = WebDriverWait(item, 10).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, 'J_ItemPic')))
                                    itemPic_id = itemPic.get_attribute('id')
                                    itemPic_data_src = itemPic.get_attribute('data-src')
                                    if not itemPic_data_src.startswith("https:"):
                                        itemPic_data_src = "https:" + itemPic_data_src
                                    itemPic_alt = itemPic.get_attribute('alt').strip()
                                    if itemPic_id == "":
                                        random_serial = ""
                                        for _ in range(12):
                                            random_serial += str(random.randint(0, 10))
                                        itemPic_id = "J_Itemlist_Pic_" + random_serial

                                    Logger.info("正在爬取第{0}家店铺的商品图片...".format(j + 1))
                                    try:
                                        stream = requests.get(itemPic_data_src, timeout=10, headers=self.headers)
                                    except requests.RequestException as e:
                                        Logger.error(e)
                                    finally:
                                        Logger.info("第{0}家店铺的商品图片爬取完毕...".format(j + 1))
                                        try:
                                            im = Image.open(BytesIO(stream.content))
                                            if im.mode != 'RGB':
                                                im = im.convert('RGB')
                                            im.save("TBTracker_Temp/{0}.jpeg".format(itemPic_id))
                                            Logger.info("第{0}家店铺的商品图片保存完毕...".format(j + 1))
                                            self.taobaoDataTable.setSpan(j * 6, 0, 6, 1)
                                            imageLabel[j].setPixmap(QPixmap.fromImage(QImage("TBTracker_Temp/{0}.jpeg".format(itemPic_id)).scaled(int(230 * 0.7), int(230 * 0.7))))
                                            imageLabel[j].setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                                            self.taobaoDataTable.setCellWidget(j * 6, 0, imageLabel[j])
                                        except Exception as e:
                                            Logger.error(e)
                                    
                                    item_price_and_link = WebDriverWait(item, 10).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, 'J_ClickStat'))
                                    )

                                    item_match_price = item_price_and_link.get_attribute('trace-price')
                                    item_link = item_price_and_link.get_attribute('href')
                                    if not item_link.startswith("https:"):
                                        item_link = "https:" + item_link
                                    self.URLList.append(item_link)

                                    status_code = requests.get(item_link).status_code
                                    Logger.info(status_code)
                                    if status_code == 200:
                                        item_title, item_price, item_taobao_price = self.find_out_real_price(j+1, item_link, item_match_price)
                                        Logger.info('第{0}家店铺的商品价格和链接爬取完毕...'.format(j + 1))
                                        self.taobaoDataTable.setSpan(j * 6, 1, 1, 2)
                                        titleItem[j].setData(Qt.DisplayRole, QVariant(item_title))
                                        titleItem[j].setFont(self.table_1_Font)
                                        titleItem[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                                        self.taobaoDataTable.setItem(j * 6, 1, titleItem[j])

                                        priceItem[j].setFont(self.table_2_Font)
                                        priceItem[j].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                                        self.taobaoDataTable.setItem(j * 6 + 3, 1, priceItem[j])
                                        priceValueItem[j].setData(Qt.DisplayRole, QVariant(item_price))
                                        self.taobaoDataTable.setItem(j * 6 + 3, 2, priceValueItem[j])

                                        tbPriceItem[j].setFont(self.table_2_Font)
                                        tbPriceItem[j].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                                        self.taobaoDataTable.setItem(j * 6 + 4, 1, tbPriceItem[j])
                                        tbPriceValueItem[j].setData(Qt.DisplayRole, QVariant(item_taobao_price))
                                        self.taobaoDataTable.setItem(j * 6 + 4, 2, tbPriceValueItem[j])
                                    else:
                                        Logger.warn('第{0}家店铺的商品价格和链接爬取失败...'.format(j + 1))

                                    item_deal = WebDriverWait(item, 10).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, 'deal-cnt'))).text.strip()
                                    Logger.info('第{0}家店铺的商品交易量爬取完毕...'.format(j + 1))
                                    dealItem[j].setFont(self.table_2_Font)
                                    dealItem[j].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                                    self.taobaoDataTable.setItem(j * 6 + 5, 1, dealItem[j])
                                    dealValueItem[j].setData(Qt.DisplayRole, QVariant(item_deal))
                                    self.taobaoDataTable.setItem(j * 6 + 5, 2, dealValueItem[j])

                                    row_3 = WebDriverWait(item, 10).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, 'row-3')))
                                    item_shop_name = WebDriverWait(row_3, 10).until(
                                        EC.presence_of_all_elements_located((By.TAG_NAME, 'span')))[4].text.strip()
                                    Logger.info('第{0}家店铺的商铺名爬取完毕...'.format(j + 1))
                                    shopItem[j].setFont(self.table_2_Font)
                                    shopItem[j].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                                    self.taobaoDataTable.setItem(j * 6 + 1, 1, shopItem[j])
                                    shopValueItem[j].setData(Qt.DisplayRole, QVariant(item_shop_name))
                                    self.taobaoDataTable.setItem(j * 6 + 1, 2, shopValueItem[j])

                                    item_location = WebDriverWait(row_3, 10).until(
                                        EC.presence_of_element_located((By.CLASS_NAME, 'location'))).text.strip()
                                    Logger.info('第{0}家店铺的货源地爬取完毕...'.format(j + 1))
                                    if item_location == "":
                                        item_location = "抓取为空"
                                    sourceItem[j].setFont(self.table_2_Font)
                                    sourceItem[j].setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                                    self.taobaoDataTable.setItem(j * 6 + 2, 1, sourceItem[j])
                                    sourceValueItem[j].setData(Qt.DisplayRole, QVariant(item_location))
                                    self.taobaoDataTable.setItem(j * 6 + 2, 2, sourceValueItem[j])

                                    isJoinedItem[j].setFont(self.table_1_Font)
                                    isJoinedItem[j].setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                                    self.taobaoDataTable.setItem(j * 6, 3, isJoinedItem[j])
                                    self.taobaoDataTable.setSpan(j * 6 + 1, 3, 5, 1)
                                    checkItem[j].setCheckState(False)
                                    self.taobaoDataTable.setItem(j * 6 + 1, 3, checkItem[j])

                                    self.progressBar.setValue(math.ceil(((j + 1)/self.returnCNT) * 100))                              
                                except Exception as e:
                                    Logger.error(e)
                            messageDialog = MessageDialog()
                            messageDialog.information(self, "消息提示对话框", "数据爬取完毕!")
                            Logger.info("数据爬取完毕")
                            webDriver.close()
                        except NoSuchElementException as e:
                            webDriver.close()
                            Logger.error(e)
                    except NoSuchElementException as e:
                        webDriver.close()
                        Logger.error(e)
                except TimeoutException as e:
                    webDriver.close()
                    Logger.error(e)
            except WebDriverException as e:
                Logger.error(e)
        else:
            messageDialog = MessageDialog()
            messageDialog.warning(self, "消息提示对话框", "请先输入搜索词!")
        
    def save_product_id(self):
        productID = self.productIDLineEdit.text().strip()
        if productID != "":
            conn = sqlite.connect('TBTracker_DB/TBTrackerTag.db')
            c = conn.cursor()
            c.execute('select count(*) from tag where TagName="{}"'.format(productID))
            count = c.fetchone()[0]
            if count == 0:
                c.execute('insert into tag values ("{}", "{}")'.format(productID, get_current_system_time()))
                conn.commit()
                c.close()
                messageDialog = MessageDialog()
                messageDialog.information(self, "消息提示对话框", "标识成功入库!")
            else:
                messageDialog = MessageDialog()
                messageDialog.information(self, "消息提示对话框", "标识已经存在!")
        else:
            messageDialog = MessageDialog()
            messageDialog.warning(self, "消息提示对话框", "请先填写商品标识!")

    def update_data(self):
        try:
            for j in range(self.returnCNT):
                flag = self.taobaoDataTable.item(j * 6 + 1, 3).checkState()
                if flag == 2:
                    conn = sqlite.connect('TBTracker_DB/TBTracker.db')
                    c = conn.cursor()
                    c.execute('insert into product values ("{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(
                        self.productIDLineEdit.text(),
                        self.URLList[j],
                        self.taobaoDataTable.item(j * 6, 1).text(),
                        self.taobaoDataTable.item(j * 6 + 1, 2).text(),
                        self.taobaoDataTable.item(j * 6 + 3, 2).text(),
                        self.taobaoDataTable.item(j * 6 + 4, 2).text(), 
                        get_current_system_time()))
                    conn.commit()
                    c.close()
            messageDialog = MessageDialog()
            messageDialog.information(self, "消息提示对话框", "数据成功入库!") 

            self.show_database()
        except AttributeError as e:
            messageDialog = MessageDialog()
            messageDialog.warning(self, "消息提示对话框", "未选择任何待导入的数据！") 

    def show_database(self):
        conn = sqlite.connect('TBTracker_DB/TBTracker.db')
        c = conn.cursor()
        c.execute('select * from product order by CreateTime desc')
        queries = c.fetchall()
        self.DBCNT = len(queries)
        c.close()
        self.DBTable.setRowCount(self.DBCNT)
        for j in range(self.DBCNT):
            self.DBTable.setItem(j, 0, QTableWidgetItem(queries[j][0]))
            self.DBTable.setItem(j, 1, QTableWidgetItem(queries[j][2]))
            self.DBTable.setItem(j, 2, QTableWidgetItem(queries[j][3]))
            self.DBTable.setItem(j, 3, QTableWidgetItem(queries[j][4]))
            self.DBTable.setItem(j, 4, QTableWidgetItem(queries[j][5]))
            flag = QTableWidgetItem()
            flag.setCheckState(False)
            self.DBTable.setItem(j, 5, flag)

    def add_data(self):
        pass

    def delete_data(self):
        notDeleteCNT = 0
        for j in range(self.DBCNT):
            flag = self.DBTable.item(j, 5).checkState()
            if flag == Qt.Checked:
                conn = sqlite.connect('TBTracker_DB/TBTracker.db')
                c = conn.cursor()
                c.execute('delete from product where ProductName="{}" and Title="{}" and ShopName="{}" and Price="{}"'.format(
                    self.DBTable.item(j, 0).text(), 
                    self.DBTable.item(j, 1).text(), 
                    self.DBTable.item(j, 2).text(), 
                    self.DBTable.item(j, 3).text()))
                conn.commit()
                c.close()
            else:
                notDeleteCNT += 1
        if notDeleteCNT == self.DBCNT:
            messageDialog = MessageDialog()
            messageDialog.warning(self, "消息提示对话框", "无效操作!")
        else:
            self.show_database()

    def plot_word_cloud(self):
        conn = sqlite.connect('TBTracker_DB/TBTrackerTag.db')
        c = conn.cursor()
        c.execute('select * from tag')
        tagQueries = c.fetchall()
        c.close()

        conn = sqlite.connect('TBTracker_DB/TBTracker.db')
        c = conn.cursor()
        wordFreq = []
        for tagQuery in tagQueries:
            c.execute('select count(*) from product where ProductName="{}"'.format(tagQuery[0]))
            wordFreq.append((tagQuery[0], c.fetchone()[0]))
        c.close()

        if len(wordFreq) != 0:
            wc = WordCloud(
                font_path="TBTracker_Font/wqy-microhei.ttc",
                width=520, 
                height=280,
                margin=10,
                max_words=500,
                background_color='white',
                max_font_size=50
            ).fit_words(wordFreq)
            wc.to_file("TBTracker_Ui/WordCloud.png")

            self.wordCloudLabel.setPixmap(QPixmap.fromImage(QImage("TBTracker_Ui/WordCloud.png")))

    def plot_product_tree(self):
        conn = sqlite.connect('TBTracker_DB/TBTrackerTag.db')
        c = conn.cursor()
        c.execute('select * from tag')
        tagQueries = c.fetchall()
        c.close()

        conn = sqlite.connect('TBTracker_DB/TBTracker.db')
        c = conn.cursor()
        roots = [QTreeWidgetItem(self.productTree) for _ in range(len(tagQueries))]
        for i, tagQuery in enumerate(tagQueries):
            roots[i].setText(0, tagQuery[0])
            roots[i].setFont(0, self.table_2_Font)
            roots[i].setCheckState(0, False)

            c.execute('select ShopName from product where ProductName="{}"'.format(tagQuery[0]))
            shopNames = list(set([query[0] for query in c.fetchall()]))
            childs = [QTreeWidgetItem(roots[i]) for _ in range(len(shopNames))]
            for j, child in enumerate(childs):
                child.setText(0, shopNames[j])
                child.setFont(0, self.table_1_Font)
                child.setCheckState(0, False)
                c.execute('select count(*) from product where ProductName="{}" and ShopName="{}"'.format(tagQuery[0], shopNames[j]))
                child.setText(1, str(c.fetchone()[0]))
            
            self.productTree.addTopLevelItem(roots[i])

        c.close()

    def select_all(self):
        currentTopLevelItemIndex = 0
        it = QTreeWidgetItemIterator(self.productTree)
        while it.value():
            if it.value() is self.productTree.topLevelItem(currentTopLevelItemIndex):
                currentTopLevelItemIndex += 1
                if it.value().checkState(0) == Qt.Checked:
                    for _ in range(it.value().childCount()):
                        it = it.__iadd__(1)
                        it.value().setCheckState(0, Qt.Checked)
            it = it.__iadd__(1)

    def export_data(self):
        mainDirectory = check_os()
        currentFileDialog = SaveFileDialog()
        fileName, filetype = currentFileDialog.save_file(self, caption="手动保存数据", directory=mainDirectory, filter="Excel Files (*.xlsx)")

        conn = sqlite.connect('TBTracker_DB/TBTracker.db')
        c = conn.cursor()

        currentTopLevelItemIndex = 0
        exportDataList = []
        it = QTreeWidgetItemIterator(self.productTree)
        while it.value():
            if it.value() is self.productTree.topLevelItem(currentTopLevelItemIndex):
                currentTopLevelItemIndex += 1
            else:
                if it.value().checkState(0) == Qt.Checked:
                    c.execute('select * from product where ProductName="{}" and ShopName="{}"'.format(
                        it.value().parent().text(0),
                        it.value().text(0)))
                    queries = c.fetchall()
                    exportDataList += queries
            it = it.__iadd__(1)
        
        excel = xlwt.Workbook()
        sheet = excel.add_sheet('淘宝商品数据', cell_overwrite_ok=True)
        sheet.write(0, 0, "商品标识")
        sheet.write(0, 1, "URL")
        sheet.write(0, 2, "标题")
        sheet.write(0, 3, "店铺名")
        sheet.write(0, 4, "价格")
        sheet.write(0, 5, "淘宝价")
        sheet.write(0, 6, "上次更新时间")
        for i, data in enumerate(exportDataList):
            sheet.write(i + 1, 0, data[0])
            sheet.write(i + 1, 1, data[1])
            sheet.write(i + 1, 2, data[2])
            sheet.write(i + 1, 3, data[3])
            sheet.write(i + 1, 4, data[4])
            sheet.write(i + 1, 5, data[5])
            sheet.write(i + 1, 6, data[6])
        excel.save("{}.xlsx".format(fileName))

    def do_the_plot(self, dateList, priceList):
        # dateList = generate_date_list((2016, 12, 1), (2017, 1, 1))
        # priceList = [random.randint(100, 300) for _ in range(len(dateList))]
        
        self.historyDataCanvas.axes.plot_date(dateList, priceList, 'r-o', linewidth=2)
        self.historyDataCanvas.axes.xaxis_date()
        self.historyDataCanvas.axes.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m-%d'))
        self.historyDataCanvas.axes.set_xticks(dateList)
        self.historyDataCanvas.axes.set_xticklabels(dateList, rotation=90, fontsize=6)
        self.historyDataCanvas.axes.set_xlabel("时间轴", fontproperties=FONT, fontsize=10)
        # self.historyDataCanvas.axes.set_yticks([100 * i for i in range(11)])
        self.historyDataCanvas.axes.set_ylabel("价格数据/￥", fontproperties=FONT, fontsize=10)
        self.historyDataCanvas.axes.set_title("淘宝商品历史数据图", fontproperties=FONT, fontsize=14)
        self.historyDataCanvas.draw()

    def manual_update(self):
        import subprocess
        child = subprocess.Popen(["sudo", "python3", "TBTracker_RoutineSpider.py"])
        child.wait()
        messageDialog = MessageDialog()
        messageDialog.information(self, "消息提示对话框", "手动更新完毕!")

    def select_commodity(self):
        pass

    def select_month(self):
        pass

    def select_year(self):
        pass
    
    # def init_config(self):
    #     with open('config.yaml', 'r') as fd:
    #         yamlFile = yaml.load(fd)
    #         smtpServerEmail = yamlFile['SMTPServer']['Email']
    #         smtpServerPassWord = yamlFile['SMTPServer']['PassWord']
    #         destinationEmail = yamlFile['Destination']['Email']
    #     self.configTextEdit.append('SMTPServer Email:\n{}\n'.format(smtpServerEmail))
    #     self.configTextEdit.append('SMTPServer PassWord:\n{}\n'.format(smtpServerPassWord))
    #     self.configTextEdit.append('Destination Email:\n{}'.format(destinationEmail))

    # def change_configuration(self):
    #     if self.configTextEdit.isReadOnly():
    #         self.changeConfigButton.setText("确认配置")
    #         self.configTextEdit.setReadOnly(False)
    #     else:
    #         self.changeConfigButton.setText("更改配置")
    #         self.configTextEdit.setReadOnly(True)

    def eventFilter(self, source, event):
        if event.type() == QEvent.MouseButtonPress:
            pass
        return QWidget.eventFilter(self, source, event)
        

class TBTrackerAddDataWindow(QWidget):
    def __init__(self):
        super(TBTrackerAddDataWindow, self).__init__()
        self.create_main_window()

    def create_main_window(self):
        self.setWindowTitle("添加数据")
        self.setWindowIcon(QIcon('TBTracker_Ui/python.png'))
        self.setMinimumSize(500, 350)
        self.setMaximumSize(500, 350)
        self.set_widgets()
        self.setLayout(self.layout)

    def set_widgets(self):
        self.productIDLineEdit = QLineEdit()
        self.URLLineEdit = QLineEdit()
        self.titleLineEdit = QLineEdit()
        self.shopNameLineEdit = QLineEdit()
        self.priceLineEdit = QLineEdit()
        self.taobaoPriceLineEdit = QLineEdit()
        self.createTimeLineEdit = QLineEdit()

        inputLayout = QGridLayout()
        inputLayout.addWidget(QLabel("商品标识"), 0, 0, 1, 1)
        inputLayout.addWidget(self.productIDLineEdit, 0, 1, 1, 3)
        inputLayout.addWidget(QLabel("URL"), 1, 0, 1, 1)
        inputLayout.addWidget(self.URLLineEdit, 1, 1, 1, 3)
        inputLayout.addWidget(QLabel("标题"), 2, 0, 1, 1)
        inputLayout.addWidget(self.titleLineEdit, 2, 1, 1, 3)
        inputLayout.addWidget(QLabel("店铺名"), 3, 0, 1, 1)
        inputLayout.addWidget(self.shopNameLineEdit, 3, 1, 1, 3)
        inputLayout.addWidget(QLabel("价格"), 4, 0, 1, 1)
        inputLayout.addWidget(self.priceLineEdit, 4, 1, 1, 3)
        inputLayout.addWidget(QLabel("淘宝价"), 5, 0, 1, 1)
        inputLayout.addWidget(self.taobaoPriceLineEdit, 5, 1, 1, 3)

        self.confirmButton = ConfirmButton()
        self.confirmButton.clicked.connect(self.confirm)
        cancelButton = CancelButton()
        cancelButton.clicked.connect(self.cancel)

        operateLayout = QHBoxLayout()
        operateLayout.addStretch()
        operateLayout.setSpacing(20)
        operateLayout.addWidget(self.confirmButton)
        operateLayout.addWidget(cancelButton)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(50, 20, 50, 20)
        self.layout.setSpacing(10)
        self.layout.addLayout(inputLayout)
        self.layout.addLayout(operateLayout)

    def confirm(self):
        pass

    def cancel(self):
        self.close()

class TBTrackerSelectCommodityWindow(QWidget):
    def __init__(self):
        super(TBTrackerSelectCommodityWindow, self).__init__()
        self.create_main_window()

    def create_main_window(self):
        self.setWindowTitle("选择商品")
        self.setWindowIcon(QIcon('TBTracker_Ui/python.png'))
        self.setMinimumSize(700, 350)
        self.setMaximumSize(700, 350)
        self.set_widgets()
        self.setLayout(self.layout)

    def set_widgets(self):
        self.pull_all_commodities()

        self.confirmButton = ConfirmButton()
        cancelButton = CancelButton()
        cancelButton.clicked.connect(self.cancel)
        operateLayout = QHBoxLayout()
        operateLayout.addStretch()
        operateLayout.setSpacing(20)
        operateLayout.addWidget(self.confirmButton)
        operateLayout.addWidget(cancelButton)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(40, 20, 40, 20)
        self.layout.setSpacing(10)
        self.layout.addWidget(self.commodityTable)
        self.layout.addLayout(operateLayout)

    def confirm(self):
        pass

    def cancel(self):
        self.close()

    def pull_all_commodities(self):
        conn = sqlite.connect('TBTracker_DB/TBTracker.db')
        c = conn.cursor()
        c.execute('select Title from product')
        titleQueries = c.fetchall()
        c.close()

        self.commodityTable = QTableWidget(len(titleQueries), 2)
        self.commodityTable.horizontalHeader().hide()
        self.commodityTable.verticalHeader().hide()
        self.commodityTable.setSelectionMode(QAbstractItemView.NoSelection)
        self.commodityTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.commodityTable.setColumnWidth(0, 25)
        self.commodityTable.setColumnWidth(1, 577)

        radioButtonList = [QRadioButton() for i in range(len(titleQueries))]
        commodityList =  [QTableWidgetItem(titleQueries[i][0]) for i in range(len(titleQueries))]
        for i in range(len(titleQueries)):
            self.commodityTable.setCellWidget(i, 0, radioButtonList[i])
            self.commodityTable.setItem(i, 1, commodityList[i])


class TBTrackerSelectMonthWindow(QWidget):
    def __init__(self):
        super(TBTrackerSelectMonthWindow, self).__init__()
        self.create_main_window()

    def create_main_window(self):
        self.setWindowTitle("选择月份")
        self.setWindowIcon(QIcon('TBTracker_Ui/python.png'))
        self.setMinimumSize(250, 100)
        self.setMaximumSize(250, 100)
        self.set_widgets()
        self.setLayout(self.layout)

    def set_widgets(self):
        self.monthComboBox = QComboBox()
        monthList = ["一月份数据", "二月份数据", "三月份数据", "四月份数据",
                     "五月份数据", "六月份数据", "七月份数据", "八月份数据",
                     "九月份数据", "十月份数据", "十一月份数据", "十二月份数据"] 
        self.monthComboBox.addItems(monthList)

        self.confirmButton = ConfirmButton()
        cancelButton = CancelButton()
        cancelButton.clicked.connect(self.cancel)
        operateLayout = QHBoxLayout()
        operateLayout.addStretch()
        operateLayout.setSpacing(20)
        operateLayout.addWidget(self.confirmButton)
        operateLayout.addWidget(cancelButton)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20,10)
        self.layout.setSpacing(10)
        self.layout.addWidget(self.monthComboBox)
        self.layout.addLayout(operateLayout)

    def confirm(self):
        pass

    def cancel(self):
        self.close()


class TBTrackerSelectYearWindow(QWidget):
    def __init__(self):
        super(TBTrackerSelectYearWindow, self).__init__()
        self.create_main_window()

    def create_main_window(self):
        self.setWindowTitle("选择年份")
        self.setWindowIcon(QIcon('TBTracker_Ui/python.png'))
        self.setMinimumSize(250, 100)
        self.setMaximumSize(250, 100)
        self.set_widgets()
        self.setLayout(self.layout)

    def set_widgets(self):
        self.yearComboBox = QComboBox()
        yearList = ["2017"]
        self.yearComboBox.addItems(yearList)

        self.confirmButton = ConfirmButton()
        cancelButton = CancelButton()
        cancelButton.clicked.connect(self.cancel)
        operateLayout = QHBoxLayout()
        operateLayout.addStretch()
        operateLayout.setSpacing(20)
        operateLayout.addWidget(self.confirmButton)
        operateLayout.addWidget(cancelButton)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(20, 20, 20, 10)
        self.layout.setSpacing(10)
        self.layout.addWidget(self.yearComboBox)
        self.layout.addLayout(operateLayout)

    def confirm(self):
        pass

    def cancel(self):
        self.close()
    