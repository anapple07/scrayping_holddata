# -*- coding: utf-8 -*-

import urllib.request
import pprint
import sys
import MySQLdb
import datetime
from MySQLdb.cursors import DictCursor
from bs4 import BeautifulSoup

args = {"host": "",
        "db": "",
        "user": "",
        "passwd": "",
        "charset": "utf8",
}


def get_html(url):

    response = urllib.request.urlopen(url)
    html = response.read().decode('utf-8')
    soup = BeautifulSoup(html,"html.parser")

    return soup


url = "http://www2.keiba.go.jp/KeibaWeb/TodayRaceInfo/TodayRaceInfoTop"
soup = get_html(url)


race_top_hold_lists = soup.select('.dbdata3')

kaisai_list = []
kaisaidata = race_top_hold_lists[1].find_all("a")

if len(kaisaidata) > 0:

    today = datetime.date.today()
    date = today.isoformat()

    for hold_list in kaisaidata:
        place = hold_list.find("span").text

        with MySQLdb.connect(**args) as cur:
            cur.execute("SET NAMES utf8")
            cur.execute("SELECT COUNT(*) FROM local_held WHERE place_name = %s AND date = %s", (place, date))
            result = cur.fetchone()
            if result[0] > 0:
                sys.exit

        with MySQLdb.connect(**args) as cur:
            cur.execute("SET NAMES utf8")
            cur.execute("INSERT INTO local_held (place_name, date) VALUES (%s, %s)", (place, date))
            cur.execute("SELECT * FROM local_held WHERE place_name = %s AND date = %s", (place, date))
            result = cur.fetchall()
            place_held_id = result[0][0]


        race_url = "http://www2.keiba.go.jp"+ hold_list.get("href")

        races = get_html(race_url)
        race_name_list = races.select('.dbdata3 > span > a')

        race_no = 1
        for race_info in race_name_list:
            o_race_name = race_info.text
            race_name = o_race_name.strip()

            with MySQLdb.connect(**args) as cur:
                cur.execute("SET NAMES utf8")
                cur.execute("SELECT COUNT(*) FROM local_race WHERE place_id = %s AND race_no = %s AND date = %s", (place_held_id, race_no, date))
                result = cur.fetchone()
                if result[0] > 0:
                    sys.exit

            with MySQLdb.connect(**args) as cur:
                cur.execute("SET NAMES utf8")
                cur.execute("INSERT INTO local_race (place_id,race_no,race_name,date) VALUES (%s, %s, %s, %s)", (place_held_id, race_no, race_name, date))
                cur.execute("SELECT id FROM local_race WHERE place_id = %s AND race_no = %s AND date = %s", (place_held_id, race_no, date))
                result = cur.fetchall()
                race_id = result[0][0]

            race_no += 1

            race_link = race_info.get("href")
            race_detail_url = "http://www2.keiba.go.jp" + race_info.get("href")
            race_detail = get_html(race_detail_url)
            horse_name_list = race_detail.select("span > a")

            horse_no = 1
            for horse_name_link in horse_name_list:
                o_horse_name = horse_name_link.text
                horse_name = o_horse_name.strip()

                with MySQLdb.connect(**args) as cur:
                    cur.execute("SET NAMES utf8")
                    cur.execute("SELECT COUNT(*) FROM local_horse WHERE race_id = %s AND horse_no = %s", (race_id, horse_no))
                    result = cur.fetchone()
                    if result[0] > 0:
                        sys.exit

                with MySQLdb.connect(**args) as cur:
                    cur.execute("SET NAMES utf8")
                    cur.execute("INSERT INTO local_horse (race_id,horse_no,horse_name) VALUES (%s, %s, %s)", (race_id, horse_no, horse_name))

                horse_no += 1
