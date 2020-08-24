import sqlite3
from contextlib import closing
from utils_sourse import *

class LandDatabase:
  def __init__(self, db_name, table_name):
    self.db_name = db_name
    self.table_name = table_name
  
  def create_table(self):
    conn = sqlite3.connect(self.db_name)
    c = conn.cursor()
    create_table = """
      create table if not exists {}(
        id integer primary key autoincrement,
        url text,
        land_image_url text,
        address text,
        price text,
        train text,
        full_station_min text,
        station text,
        walk_min text,
        distance text,
        land_area text,
        present_situation text,
        ownership text,
        land_type text,
        city_plan text,
        construct_condition text,
        roadway text,
        coverage_ratio text,
        floor_area_ratio text,
        area_of_use text,
        trade_type text,
        crawl_date text,
        renew_date text,
        extra text
      )
      """.format(self.table_name)
    c.execute(create_table)
    conn.commit()
    conn.close()

  def exists(self, url):
    conn = sqlite3.connect(self.db_name)
    c = conn.cursor()
    search_sql = "select * from {} where url=?".format(self.table_name)
    c.execute(search_sql, (url,))
    search_result = c.fetchall()
    conn.close()
    return len(search_result) > 0

  def select_all_by_date(self, date):
    conn = sqlite3.connect(self.db)
    c = conn.cursor()
    search_sql =  "select * from {} where url=?".format(self.table_name)
    c.execute(search_sql, (date,))
    search_result = c.fetchall()
    return search_result

  def insert_record(self, date):
    conn = sqlite3.connect(self.db_name)
    conn.row_factory = dict_factory
    c = conn.cursor()
    insert_sql = """
    insert into {} (
      url,
      land_image_url,
      address,
      price,
      train,
      full_station_min,
      station,
      wallk_min,
      distance,
      land_area,
      present_situation,
      ownership,
      land_type,
      city_plan,
      construct_condition,
      roadway,
      coverage_ratio,
      floor_area_ratio,
      area_of_use,
      trade_type,
      crawl_date,
      renew_date,
      extra
    )
    values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """.format(self.table_name)

    insert_values = (
            date["url"],
            date["land_image_url"],
            date["address"],
            date["price"],
            date["train"],
            date["full_station_min"],
            date["station"],
            date["walk_min"],
            date["distance"],
            date["land_area"],
            date["present_situation"],
            date["ownership"],
            date["land_type"],
            date["city_plan"],
            date["construct_condition"],
            date["roadway"],
            date["coverage_ratio"],
            date["floor_area_ratio"],
            date["area_of_use"],
            date["trade_type"],
            date["crawl_date"],
            date["renew_date"],
            date["extra"],
    )

    c.execute(insert_sql, insert_values)
    conn.commit()
    conn.close()

