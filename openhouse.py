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
  output["URL"] = record[0]
  output["所在地"] = record[1]
  output["土地価格"] = "{}円".format(record[2])
  output["土地面積(平米)"] = record[3]
  output["土地面積(坪)"] = record[4]
  output["道路幅員"] = record[5]
  output["容積"] = record[6]
  output["建ぺい率"] = record[7]
  output["最寄り駅"] = record[8]
  output["徒歩分数"] = record[9]
  if data["distance"]:
    output["距離"] = record[10]
  else:
    output["距離"] = ""
  output["用途地域"] = record[11]
  output["土地権利"] = record[12]
  if data["time_at"]:
    output["取得日時"] = record[13]
  else:
    output["取得日時"] = ""
  if data["land_image_url"]:
    output["測量図URL"] = record[14]
  else:
    output["測量図URL"] = ""
  if data["extra"]:
    output["備考"] = record[15]
  else:
    output["備考"] = ""
  if data["setback"]:
    output["セットバック"] = record[16]
  else:
    output["セットバック"] = ""

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

start_url = 'https://oh.openhouse-group.com/kanto/search/area/'
browser = webdriver.Chrome()
browser.get(start_url)

time.sleep(3)

login_page = browser.find_element_by_xpath('/html/body/div[1]/div/div[4]/div/div[2]/a')
login_page.click()

time.sleep(3)

login_email = browser.find_element_by_xpath('//*[@id="email"]')
login_email.send_keys("shunki.inoue@macromeister.com")
login_password = browser.find_element_by_xpath('/html/body/div[6]/div[2]/div/div[1]/div[2]/form/div[1]/table/tbody/tr[2]/td/div/input')
login_password.send_keys("meisterpass0813")

time.sleep(5)

login_button = browser.find_element_by_xpath('/html/body/div[6]/div[2]/div/div[1]/div[2]/form/div[2]/button')
login_button.click()

time.sleep(7)

#ここに必要に応じてタグ追加

tokyo_tosin = browser.find_element_by_xpath('//*[@id="area-01"]')
tokyo_tosin.click()

tokyo_south = browser.find_element_by_xpath('//*[@id="area-02"]')
tokyo_west = browser.find_element_by_xpath('//*[@id="area-03"]')
tokyo_north = browser.find_element_by_xpath('//*[@id="area-04"]')
tokyo_east = browser.find_element_by_xpath('//*[@id="area-05"]')
tokyo_tokka = browser.find_element_by_xpath('//*[@id=area-06"]')

tokyo_south.click()
tokyo_west.click()
tokyo_north.click()
tokyo_east.click()
tokyo_tokka.click()

toti_button = browser.find_element_by_xpath(''//*[@id="form-parts-2-class_3"])
toti_button.click()

go_button = browser.find_element_by_xpath('/html/body/div[9]/div[3]/div[1]/div[3]/div[2]/button')
go_button.click()

time.sleep(5)

detail_urls = []
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

while True:
  current_page = browser.current_url
  details = browser.find_elements_by_css_selector('body > div.oh-contents.oh-contents--2col > div.oh-contents__main > div.oh-section > div.oh-itemList3 > div > div.oh-itemList3__head > div.oh-itemList3__heading > h2 > a')
  for detail in details:
    detailEle = detail.get_attribute('href')
    detail_urls.append(detailEle)
    print(detailEle)
  sleep()
  for detail_url in detail_urls:
    browser.get(detail_url)
    sleep()
    url = browser.current_url
    address_ele = browser.find_element_by_xpath('/html/body/div[6]/div[2]/div[2]/div[2]/table/tbody/tr[1]/td/div/div[1]').text
    address = address_ele.replace("[ 周辺地図 ]", "")
    price_strings = browser.find_element_by_xpath('//th[contains(text(), "価格")]/following-sibling::td[1]').text
    price_string = re.findall(r"\d+,\d+", price_strings)
    number = float(re.sub(",", "", price_string.group()))
    scale = 1
    price_ele = 0
    if "億" in price_strings:
      scale = 100000000
    elif "万" in price_strings:
      scale = 10000
    elif "千" in price_strings:
      scale = 1000
    else:
      print("億、万、千が含まれていません")
    price_ele += int(number * scale)
    price = price_ele
    square = browser.find_element_by_xpath('//th[contains(text(), "土地面積")]/following-sibling::td[1]').text
    tsubo_el = re.match(r'\d+\.?\d+', square).group()
    tsubo = float(tsubo_el) * 0.3025
    roadway = browser.find_element_by_xpath('//th[contains(text(), "接道状況")]/following-sibling::td[1]').text
    yoseki_kenpei = browser.find_element_by_xpath('//th[contains(text(), "建ぺい率／容積率")]/following-sibling::td[1]').text
    yoseki_kenpei_sp = yoseki_kenpei.split('／')
    floor_area_ratio = yoseki_kenpei_sp[0]
    coverage_ratio = yoseki_kenpei_sp[1]
    moyori_toho = browser.find_element_by_xpath('/html/body/div[9]/div[2]/div[2]/div[2]/table/tbody/tr[2]/td/div/div[1]').text
    station = re.match(r'.+駅', moyori_toho)
    walk_min_els = moyori_toho.split(" ")
    for walk_min_el in walk_min_els:
      if "徒歩" in walk_min_el:
        walk_min = walk_min_el
    distance = None
    area_of_use = broser.find_element_by_xpath('//th[contains(text(), "用途地域")]/following-sibling::td[1]').text
    ownership = browser.find_element_by_xpath('//th[contains(text(), "土地権利")]/following-sibling::td[1]').text
    time_at = browser.find_element_by_xpath('//th[contains(text(), "情報更新日")]/following-sibling::td[1]').text
    land_image_url = None
    try:
      extra = browser.find_element_by_xpath('//th[contains(text(), "備考")]/following-sibling::td[1]').text
    except:
      extra = None
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
    page = browser.find_element_by_css_selector('body > div.oh-contents.oh-contents--2col > div.oh-contents__main > div.oh-section > div:nth-child(2) > div.oh-toolbar__pager > div > a.oh-pager__item.oh-pager__next').get_attribute('href')
    browser.get(page)
    #次のページがあれば遷移
  except:
    print('クロール終了'')
    break

db = "openhouse.db"

#データベースなければ作成
conn = sqlite3.connect(db)
c = conn.cursor()
create_table = """
create table if not exists test (
  id integer primary key autoincrement,
  url text,
  address text,
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

insert_record(data)

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
write_csv("{}/openhouse_{}".format(csv_dir, date_ele), output_dict)
print("終了です")
browser.quit()