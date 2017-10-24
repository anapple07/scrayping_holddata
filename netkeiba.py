# -*- coding: utf-8 -*-

import urllib.request
import pprint
import sys
import re
from bs4 import BeautifulSoup
import MySQLdb
import datetime
from MySQLdb.cursors import DictCursor

args = {"host": "",
        "db": "",
        "user": "",
        "passwd": "",
        "charset": "utf8",
}


def get_html(url):

    response = urllib.request.urlopen(url)
    html = response.read().decode('euc-jp')
    soup = BeautifulSoup(html,"html.parser")

    return soup


today = datetime.date.today()
date = today.isoformat()

tstr = today.strftime('%m%d')

url = "http://race.netkeiba.com/?pid=race_list_sub&id=c" + tstr
soup = get_html(url)

race_top_hold_lists = soup.select('dl.race_top_hold_list')

for hold_list in race_top_hold_lists:
    kaisaidata = hold_list.select(".kaisaidata")[0].text
    race_top_data_infos = hold_list.select('.race_top_data_info')

    place = re.sub("回|日|目|[0-9]", "", kaisaidata )
    with MySQLdb.connect(**args) as cur:
        cur.execute("SET NAMES utf8")
        cur.execute("INSERT INTO centor_held (place_name, date) VALUES (%s, %s)", (place, date))
        cur.execute("SELECT * FROM centor_held WHERE place_name = %s AND date = %s", (place, date))
        result = cur.fetchall()
        place_held_id = result[0][0]

    for race_info  in race_top_data_infos:
        race_num = race_info.select("img")[0]["alt"]
        race_no  = re.sub("R", "", race_num)
        race_name = race_info.select("div.racename a")[0].text
        race_url = race_info.select("div.racename a")[0]["href"]
        race_url = re.sub("pid=race&", "pid=race_old&", race_url )

        with MySQLdb.connect(**args) as cur:
            cur.execute("SET NAMES utf8")
            cur.execute("INSERT INTO centor_race (place_id,race_no,race_name,date) VALUES (%s, %s, %s, %s)", (place_held_id, race_no, race_name, date))
            cur.execute("SELECT id FROM centor_race WHERE place_id = %s AND race_no = %s AND date = %s", (place_held_id, race_no, date))
            result = cur.fetchall()
            race_id = result[0][0]

        race_detail = get_html("http://race.netkeiba.com" + race_url)
        horse_name_list = race_detail.select(".horsename > div > a")

        horse_no = 1
        for horse in horse_name_list:
            horse_name = horse.text

            with MySQLdb.connect(**args) as cur:
                cur.execute("SET NAMES utf8")
                cur.execute("INSERT INTO centor_horse (race_id,horse_no,horse_name) VALUES (%s, %s, %s)", (race_id, horse_no, horse_name))
            horse_no += 1


#pprint.pprint(kaisai_list)
