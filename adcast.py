from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import chromedriver_binary
from utils_sourse import *
from LandD_sourse import LandDatabase
from collections import OrderedDict
import re
import sqlite3
import datetime
import sys
import os

def record_to_output(record):
  output = OrderedDict()
  output["URL"] = record[1]
  output["所在地"] = record[2]
  output["土地価格"] = str(record[3])+"円"
  output["土地面積(平米)"] = record[4]
  output["土地面積(坪)"] = record[5]
  output["道路幅員"] = record[6]
  output["容積"] = record[7]
  output["建ぺい率"] = record[8]
  output["最寄り駅"] = record[9]
  output["徒歩分数"] = record[10]
  output["距離"] = record[11]
  output["用途地域"] = record[12]
  output["土地権利"] = record[13]
  output["取得日時"] = record[16]
  output["測量図URL"] = record[15]
  output["備考"] = record[17]
  output["セットバック"] = record[18]
  return output

def insert_record(data):
  conn = sqlite3.connect(db)
  c = conn.cursor()
  insert_record = """
  insert into test (
    url,
    address,
    price,
    square,
    tsubo,
    roadway,
    floor_area_ratio,
    coverage_ratio,
    station,
    walk_min,
    distance,
    area_of_use,
    ownership,
    time_at,
    land_image_url,
    crawl_date,
    extra,
    setback
  )
  values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
  )
  """
  insert_values = (
    data['url'],
    data['address'],
    data['price'],
    data['square'],
    data['tsubo'],
    data['roadway'],
    data['floor_area_ratio'],
    data['coverage_ratio'],
    str(data['station']),
    str(data['walk_min']),
    data['distance'],
    data['area_of_use'],
    data['ownership'],
    data['time_at'],
    data['land_image_url'],
    data['crawl_date'],
    data['extra'],
    data['setback']
  )
  c.execute(insert_record, insert_values)
  conn.commit()
  conn.close()

start_url = 'https://www.ad-cast.info/sch/area_list.php?kind=1'

browser = webdriver.Chrome()
browser.get(start_url)

sleep()

elem_urls = []
detail_urls = []
page_urls = []
data = {
  "url":"",
  "address":"",
  "price":"",
  "square":"",
  "tsubo":"",
  "roadway":"",
  "floor_area_ratio":"",
  "coverage_ratio":"",
  "station":"",
  "walk_min":"",
  "distance":"",
  "area_of_use":"",
  "ownership":"",
  "time_at":"",
  "land_image_url":"",
  "crawl_date":str(datetime.date.today()),
  "extra":"",
  "setback":""
}

areas = browser.find_elements_by_css_selector('#wrapper > section > div > form > div.box_w > ul > li > a')
for area in areas:
  url = area.get_attribute('href')
  elem_urls.append(url)
  print(url)
  #東京各地域のURLを取得
for elem_url in elem_urls:
  print(elem_url)
  browser.get(elem_url)
  sleep()
  while True:
    current_page = browser.current_url
    details = browser.find_elements_by_css_selector('#list_left > div.listbox')
    for detail in details:
      detail_ele = detail.find_element_by_css_selector('div.boxhead > div.bknname > a').get_attribute('href')
      detail_urls.append(detail_ele)
      print(detail_ele)
      #詳細ページのURLを取得
    sleep()
    for detail_url in detail_urls:
      browser.get(detail_url)
      sleep()
      url = browser.current_url
      address = browser.find_element_by_xpath('//th[contains(text(), "所在地")]/following-sibling::td[1]').text
      price_strings = browser.find_element_by_xpath('//*[@id="detail_navi"]/div[1]/div[3]/span').text
      price_unit = browser.find_element_by_xpath('//*[@id="detail_navi"]/div[1]/div[3]').text
      price_string = re.match(r"\d+,\d+", price_strings)
      number = float(re.sub(",", "", price_string.group()))
      scale = 1
      price_ele = 0
      if "億" in price_unit:
        scale = 100000000
      elif "万" in price_unit:
        scale = 10000
      elif "千" in price_unit:
        scale = 1000
      else:
        print("億、万、千が含まれていません")
      price_ele += int(number * scale)
      price = price_ele
      square = browser.find_element_by_xpath('//th[contains(text(), "土地面積")]/following-sibling::td[1]').text
      tsubo_el = re.match(r'\d+\.?\d+', square).group()
      tsubo = float(tsubo_el) * 0.3025
      roadway = browser.find_element_by_xpath('//th[contains(text(), "接道")]/following-sibling::td[1]').text
      yoseki_kenpei = browser.find_element_by_xpath('//th[contains(text(), "建ぺい率／容積率")]/following-sibling::td[1]').text
      yoseki_kenpei_sp = yoseki_kenpei.split('／')
      floor_area_ratio = yoseki_kenpei_sp[0]
      coverage_ratio = yoseki_kenpei_sp[1]
      moyori_tohos = browser.find_elements_by_xpath('//th[contains(text(), "交通")]/following-sibling::td')
      trafic = []
      for moyori_toho in moyori_tohos:
        moyori_toho_ele = moyori_toho.text
        trafic.append(moyori_toho_ele)
      for trafic_ele in trafic:
        station = re.findall(r'.+駅', trafic_ele)
        walk_min = re.findall(r'「.+」.+\d+分', trafic_ele)
      trafic.clear()
      distance = None
      area_of_use = browser.find_element_by_xpath('//th[contains(text(), "用途地域")]/following-sibling::td[1]').text
      ownership = browser.find_element_by_xpath('//th[contains(text(), "土地権利")]/following-sibling::td[1]').text
      time_at = None
      land_image_url = None
      extra = browser.find_element_by_xpath('//th[contains(text(), "備考")]/following-sibling::td[1]').text
      setback = None
      data["url"] = url
      data["address"] = address
      data["price"] = price
      data["square"] = square
      data["tsubo"] = tsubo
      data["roadway"] = roadway
      data["floor_area_ratio"] = floor_area_ratio
      data["coverage_ratio"] = coverage_ratio
      data["station"] = station
      data["walk_min"] = walk_min
      data["distance"] = distance
      data["area_of_use"] = area_of_use
      data["ownership"] = ownership
      data["time_at"] = time_at
      data["land_image_url"] = land_image_url
      data["extra"] = extra
      data["setback"] = setback
    browser.get(current_page)
    detail_urls.clear()
    sleep()
    try:
      page = browser.find_element_by_css_selector('#list_left > div.page_navi > div > a.on + a').get_attribute('href')
      browser.get(page)
      #次のページがあれば遷移
    except:
      print('次の区域に移ります')
      #無ければ次の区域に遷移
      break

db = "adcast.db"

#データベースなければ作成
conn = sqlite3.connect(db)
c = conn.cursor()
create_table = """
create table if not exists test (
  id integer primary key autoincrement,
  url text,
  location text,
  price integer,
  square text,
  tsubo float,
  roadway text,
  floor_area_ratio text,
  coverage_ratio text,
  station list,
  walk_min list,
  distance text null,
  area_of_use text,
  ownership text,
  time_at text null,
  land_image_url text null,
  crawl_date text,
  extra text null,
  setback text null
)
"""
c.execute(create_table)
conn.commit()
conn.close()

#それぞれのデータ型チェック用
#print(type(data["url"]))
#print(type(data["address"]))
#print(type(data["price"]))
#print(type(data["square"]))
#print(type(data["tsubo"]))
#print(type(data["roadway"]))
#print(type(data["floor_area_ratio"]))
#print(type(data["coverage_ratio"]))
#print(type(data["station"]))
#print(type(data["walk_min"]))
#print(type(data["distance"]))
#print(type(data["area_of_use"]))
#print(type(data["ownership"]))
#print(type(data["time_at"]))
#print(type(data["land_image_url"]))
#print(type(data["crawl_date"]))
#print(type(data["extra"]))
#print(type(data["setback"]))

conn = sqlite3.connect(db)
c = conn.cursor()
search_url = "select * from test where url=?"
c.execute(search_url, (data["url"],))
search_url_rs = c.fetchall()
conn.close()
if not len(search_url_rs) > 0:
  insert_record(data)
else:
  print("既にあるデータです。")

date_ele = datetime.date.today()

#crawl_dateよりその日のクロールした結果をcsvに落とし込む
conn = sqlite3.connect(db)
c = conn.cursor()
search_sql =  "select * from test where crawl_date=?"
c.execute(search_sql, (date_ele,))
search_result = c.fetchall()

if len(search_result) == 0:
  print("強制終了です")
  sys.exit()

output_dict = []
for record in search_result:
  print(record)
  output_dict.append(record_to_output(record))

csv_dir = "csv/{}".format(date_ele)
if not os.path.exists(csv_dir):
  os.makedirs(csv_dir)
write_csv("{}/adcast_{}.csv".format(csv_dir, date_ele), output_dict)
print("終了です")
browser.quit()