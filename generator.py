# -*- coding: utf-8 -*-

#v2.25.1

import logging
logging.basicConfig(filename='log.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
try:
    import sys
    import os
    import xmltv
    import requests
    import xml.etree.ElementTree as ET
    import unicodedata
    import time
    from urllib.parse import quote
    from datetime import datetime, timedelta, date
    from ftplib import FTP
    import time
    import schedule
    from bs4 import BeautifulSoup
    from settings import*
except Exception as ex:
    print(ex)
    logging.error("365 EPG Generator - %s" % ex)
    input("Pro ukončení stiskněte libovolnou klávesu")
    sys.exit(0)


dn = os.path.dirname(os.path.realpath(__file__))
fn = os.path.join(dn,file_name)
custom_names_path = os.path.join(dn,"custom_names.txt")
now = datetime.now()
local_now = now.astimezone()
TS = " " + str(local_now)[-6:].replace(":", "")


def encode(string):
    string = str(unicodedata.normalize('NFKD', string).encode('ascii', 'ignore'), "utf-8")
    return string


custom_names = []
try:
    f = open(custom_names_path, "r", encoding="utf-8").read().splitlines()
    for x in f:
        x = x.split("=")
        custom_names.append((x[0], x[1]))
except:
    pass


def replace_names(value):
    for v in custom_names:
        if v[0] == value:
            value = v[1]
    return value


def get_stvsk_programmes(stv_ids, d, d_b):
    if d_b > 7:
        d_b = 7
    if d > 15:
        d = 15
    channels = []
    programmes = []
    stv_channels = {}
    req = requests.get("http://felixtv.wz.cz/epg/channels_sk.php").json()
    for x in req["channels"]:
        stv_channels[x["id"]] = x["name"]
    if stv_ids == "":
        stv_id = "".join('{},'.format(k) for k in stv_channels.keys())[:-1]
    else:
        stv_id = stv_ids
    for k, v in stv_channels.items():
        if k in stv_id.split(","):
            channels.append({'display-name': [(replace_names(v), u'cs')], 'id': 'stvsk-' + k,'icon': [{'src': 'https://sledovanietv.sk/cache/biglogos/' + k + '.png'}]})
    now = datetime.now()
    st = 1
    for i in range(d_b*-1, d):
        next_day = now + timedelta(days = i)
        date_from = next_day.strftime("%Y-%m-%d")
        date_ = next_day.strftime("%d.%m.%Y")
        print(date_)
        req = requests.get("http://felixtv.wz.cz/epg/stv_sk.php?ch=" + stv_id + "&d=" + date_from).json()["channels"]
        for k in req.keys():
            for x in req[k]:
                programm = {'channel': "stvsk-" + k, 'start': x["startTime"].replace("-", "").replace(" ", "").replace(":", "") + "00" + TS, 'stop': x["endTime"].replace("-", "").replace(" ", "").replace(":", "") + "00" + TS, 'title': [(x["title"], u'')], 'desc': [(x["description"], u'')]}
                try:
                    icon = x["poster"]
                except:
                    icon = None
                if icon != None:
                    programm['icon'] = [{"src": icon}]
                try:
                    genres = []
                    for g in x["genres"]:
                        genres.append((g["name"], u''))
                except:
                    genres = []
                if genres != []:
                    programm['category'] = genres
                if programm not in programmes:
                    programmes.append(programm)
        sys.stdout.write('\x1b[1A')
        print(date_ + "  OK")
    print("\n")
    return channels, programmes


def get_stv_programmes(stv_ids, d, d_b):
    if d_b > 7:
        d_b = 7
    if d > 15:
        d = 15
    channels = []
    programmes = []
    stv_channels = {}
    req = requests.get("http://felixtv.wz.cz/epg/channels.php").json()
    for x in req["channels"]:
        stv_channels[x["id"]] = x["name"]
    if stv_ids == "":
        stv_id = "".join('{},'.format(k) for k in stv_channels.keys())[:-1]
    else:
        stv_id = stv_ids
    for k, v in stv_channels.items():
        if k in stv_id.split(","):
            channels.append({'display-name': [(replace_names(v), u'cs')], 'id': 'stv-' + k,'icon': [{'src': 'https://sledovanitv.cz/cache/biglogos/' + k + '.png'}]})
    now = datetime.now()
    for i in range(d_b*-1, d):
        next_day = now + timedelta(days = i)
        date_from = next_day.strftime("%Y-%m-%d")
        date_ = next_day.strftime("%d.%m.%Y")
        print(date_)
        req = requests.get("http://felixtv.wz.cz/epg/stv.php?ch=" + stv_id + "&d=" + date_from).json()["channels"]
        for k in req.keys():
            for x in req[k]:
                programm = {'channel': "stv-" + k, 'start': x["startTime"].replace("-", "").replace(" ", "").replace(":", "") + "00" + TS, 'stop': x["endTime"].replace("-", "").replace(" ", "").replace(":", "") + "00" + TS, 'title': [(x["title"], u'')], 'desc': [(x["description"], u'')]}
                try:
                    icon = x["poster"]
                except:
                    icon = None
                if icon != None:
                    programm['icon'] = [{"src": icon}]
                try:
                    genres = []
                    for g in x["genres"]:
                        genres.append((g["name"], u''))
                except:
                    genres = []
                if genres != []:
                    programm['category'] = genres
                if programm not in programmes:
                    programmes.append(programm)
        sys.stdout.write('\x1b[1A')
        print(date_ + "  OK")
    print("\n")
    return channels, programmes


def get_ott_play_programmes(ids):
    channels = []
    f = {"7:2777": "fox-tv", "7:2779": "fox-tv", "7:2528": "fox-tv", "ITbas:SuperTennis.it": "korona"}
    ids_ = ids.split(",")
    c = {'display-name': [(replace_names('Penthouse Gold'), u'cs')], 'id': '7:2777','icon': [{'src': 'http://pics.cbilling.pw/streams/penthouse1-hd.png'}]}, {'display-name': [(replace_names('Penthouse Quickies'), u'cs')], 'id': '7:2779','icon': [{'src': 'http://pics.cbilling.pw/streams/penthouse2-hd.png'}]}, {'display-name': [(replace_names('Vivid Red'), u'cs')], 'id': '7:2528','icon': [{'src': 'http://pics.cbilling.pw/streams/vivid-red-hd.png'}]}, {'display-name': [(replace_names('Super Tennis'), u'cs')], 'id': 'ITbas:SuperTennis.it','icon': [{'src': 'https://guidatv.sky.it/logo/5246supertennishd_Light_Fit.png?checksum=13f5cbb1646d848fde3af6fccba8dd4c'}]}
    for x in c:
        if x["id"] in ids_:
            channels.append(x)
    programmes = []
    headers = {"User-Agent": "Mozilla/5.0 (Linux; U; Android 12; cs-cz; Xiaomi 11 Lite 5G NE Build/SKQ1.211006.001) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.116 Mobile Safari/537.36 XiaoMi/MiuiBrowser/12.16.3.1-gn", "Host": "epg.ott-play.com", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "Connection": "keep-alive"}
    for id in ids_:
        r = requests.get("http://epg.ott-play.com/php/show_prog.php?f=" + f[id] + "/epg/" + id + ".json", headers = headers)
        soup = BeautifulSoup(r.text, "html.parser")
        table = soup.find_all('table')[0]
        tr = table.find_all("tr")
        data = []
        for td in tr:
           cols = td.find_all("td")
           cols = [ele.text.strip() for ele in cols]
           data.append([ele for ele in cols if ele])
        for d in data[1:]:
            dat = d[0].split("/")
            dat = dat[2] + dat[1] + dat[0]
            ts = d[1][:5].replace(":", "") + "00"
            te = d[1][6:11].replace(":", "") + "00"
            timestart = dat + ts
            timeend = dat + te
            title = d[2]
            try:
                if "|" in d[3]:
                    descr = d[3].split(" | ")[1][2:]
                else:
                    descr = d[3]
            except:
                descr = ""
            programmes.append({"channel": id, "start": timestart + TS, "stop": timeend + TS, "title": [(title, "")], "desc": [(descr, u'')]})
    print("OK\n")
    return channels, programmes


def get_tv_spiel_programmes(ids, d, d_b):
    ids = ids.split(",")
    if d_b > 7:
        d_b = 7
    if d > 14:
        d = 14
    channels = []
    programmes = []
    ids_ = {'display-name': [(replace_names('Eurosport 1 (DE)'), u'cs')], 'id': 'EURO','icon': [{'src': 'http://live.tvspielfilm.de/static/images/channels/large/EURO.png'}]}, {'display-name': [(replace_names('Eurosport 2 (DE)'), u'cs')], 'id': 'EURO2','icon': [{'src': 'http://live.tvspielfilm.de/static/images/channels/large/EURO2.png'}]}, {'display-name': [(replace_names('Sky Sport 1 (DE)'), u'cs')], 'id': 'HDSPO','icon': [{'src': 'http://live.tvspielfilm.de/static/images/channels/large/HDSPO.png'}]}, {'display-name': [(replace_names('Sky Sport 2 (DE)'), u'cs')], 'id': 'SHD2','icon': [{'src': 'http://live.tvspielfilm.de/static/images/channels/large/SHD2.png'}]}, {'display-name': [(replace_names('Sky Sport Austria1'), u'cs')], 'id': 'SPO-A','icon': [{'src': 'http://live.tvspielfilm.de/static/images/channels/large/SPO-A.png'}]}, {'display-name': [(replace_names('ORF Sport+'), u'cs')], 'id': 'ORFSP','icon': [{'src': 'http://live.tvspielfilm.de/static/images/channels/large/ORFSP.png'}]}
    for x in ids_:
        if x["id"] in ids:
            channels.append(x)
    now = datetime.now()
    for x in range(d_b*-1, d):
        next_day = now + timedelta(days = x)
        date_ = next_day.strftime("%d.%m.%Y")
        date = next_day.strftime("%Y-%m-%d")
        print(date_)
        for y in ids:
            html = requests.get("https://live.tvspielfilm.de/static/broadcast/list/" + y + "/" + date).json()
            for x in html:
                start = time.strftime('%Y%m%d%H%M%S', time.localtime(int(x['timestart'])))
                stop = time.strftime('%Y%m%d%H%M%S', time.localtime(int(x['timeend'])))
                try:
                    desc = x['text']
                except:
                    desc = ""
                programm = {"channel": y, "start": str(start) + TS, "stop": str(stop) + TS, "title": [(x['title'], "")], "desc": [(desc, u'')]}
                try:
                    icon = x["images"][0]["size2"]
                except:
                    icon = None
                if icon != None:
                    programm['icon'] = [{"src": icon}]
                if programm not in programmes:
                    programmes.append(programm)
        sys.stdout.write('\x1b[1A')
        print(date_ + "  OK")
    print("\n")
    return channels, programmes


def get_muj_tv_programmes(ids, d, d_b):
    ids = ids.split(",")
    if d_b > 1:
        d_b = 1
    if d > 10:
        d = 10
    channels = []
    programmes = []
    ids_ = {'723': '723-skylink-7', '233': '233-stingray-classica', '234': '234-stingray-iconcerts', '110': '110-stingray-cmusic', '40': '40-orf1', '41': '41-orf2', '49': '49-rtl', '50': '50-rtl2', '39': '39-polsat', '37': '37-tvp1', '38': '38-tvp2', '174': '174-pro7', '52': '52-sat1', '54': '54-kabel1', '53': '53-vox', '393': '393-zdf', '216': '216-zdf-neo', '46': '46-3sat', '408': '408-sat1-gold', '892': '892-vixen', '1040': '1040-canal+sport'}
    channels = []
    c = {'display-name': [(replace_names('Skylink 7'), u'cs')], 'id': '723-skylink-7','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=ac6c69625699eaecc9b39f7ea4d69b8c&amp;p2=80'}]}, {'display-name': [(replace_names('Stingray Classica'), u'cs')], 'id': '233-stingray-classica','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=661af53f8f3b997611c29f844c7006fd&amp;p2=80'}]}, {'display-name': [(replace_names('Stingray iConcerts'), u'cs')], 'id': '234-stingray-iconcerts','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=99c87946872c81f46190c77af7cd1d89&amp;p2=80'}]}, {'display-name': [(replace_names('Stingray CMusic'), u'cs')], 'id': '110-stingray-cmusic','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=b323f2ad3200cb938b43bed58dd8fbf9&amp;p2=80'}]}, {'display-name': [(replace_names('ORF1'), u'cs')], 'id': '40-orf1','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=422162d3082a84fc97a7fb9b3ad6823f&amp;p2=80'}]}, {'display-name': [(replace_names('ORF2'), u'cs')], 'id': '41-orf2','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=477dcc38e54309f5db7aec56b62b4cdf&amp;p2=80'}]}, {'display-name': [(replace_names('RTL'), u'cs')], 'id': '49-rtl','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=7cb9005e66956c56fd0671ee79ee2471&amp;p2=80'}]}, {'display-name': [(replace_names('RTL2'), u'cs')], 'id': '50-rtl2','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=418e0d04529ea3aaa2bc2c925ddf5982&amp;p2=80'}]}, {'display-name': [(replace_names('Polsat'), u'cs')], 'id': '39-polsat','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=f54e290782e8352303cfe43ce949d339&amp;p2=80'}]}, {'display-name': [(replace_names('TVP1'), u'cs')], 'id': '37-tvp1','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=770431539d1fa662f705c1c05a0dd943&amp;p2=80'}]}, {'display-name': [(replace_names('TVP2'), u'cs')], 'id': '38-tvp2','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=e2ce4065f27ce199f7613f38878cef72&amp;p2=80'}]}, {'display-name': [(replace_names('Pro7'), u'cs')], 'id': '174-pro7','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=e23a7fb8caff9ff514f254c43a39d9b6&amp;p2=80'}]}, {'display-name': [(replace_names('SAT1'), u'cs')], 'id': '52-sat1','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=97dd916e0164fff141065c3fba71c291&amp;p2=80'}]}, {'display-name': [(replace_names('Kabel1'), u'cs')], 'id': '54-kabel1','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=be6dc88dd3c1c243ba4f28cccb8f1d34&amp;p2=80'}]}, {'display-name': [(replace_names('VOX'), u'cs')], 'id': '53-vox','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=d2c68d2b145a5f2e20e5c05c20a9679e&amp;p2=80'}]}, {'display-name': [(replace_names('ZDF'), u'cs')], 'id': '393-zdf','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=dad48d516fbdb30321564701cc3faa04&amp;p2=80'}]}, {'display-name': [(replace_names('ZDF Neo'), u'cs')], 'id': '216-zdf-neo','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=cd5b8935893b0e4cde41bc3720435f14&amp;p2=80'}]}, {'display-name': [(replace_names('3SAT'), u'cs')], 'id': '46-3sat','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=58d350c6065d9355a52c6dbc3b31b185&amp;p2=80'}]}, {'display-name': [(replace_names('SAT.1 GOLD'), u'cs')], 'id': '408-sat1-gold','icon': [{'src': ''}]}, {'display-name': [(replace_names('Vixen'), u'cs')], 'id': '892-vixen','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=4499ebafb26a915859febcb4306703ca&amp;p2=80'}]}, {'display-name': [(replace_names('Canal+ Sport'), u'cs')], 'id': '1040-canal+sport','icon': [{'src': 'https://services.mujtvprogram.cz/tvprogram2services/services/logoImageDownloader.php?p1=ab73879fdf9b10e1deb0224bfbb3cfd8&amp;p2=80'}]}
    for x in c:
        if x["id"].split("-")[0] in ids:
            channels.append(x)
    now = datetime.now()
    for x in range(d_b*-1, d):
        next_day = now + timedelta(days = x)
        date_ = next_day.strftime("%d.%m.%Y")
        print(date_)
        for y in ids:
            html = requests.post("https://services.mujtvprogram.cz/tvprogram2services/services/tvprogrammelist_mobile.php", data = {"channel_cid": y, "day": str(x)}).content
            root = ET.fromstring(html)
            for i in root.iter("programme"):
                programmes.append({"channel": ids_[y],  "start": time.strftime('%Y%m%d%H%M%S', time.localtime(int(i.find("startDateTimeInSec").text))) + TS, "stop": time.strftime('%Y%m%d%H%M%S', time.localtime(int(i.find("endDateTimeInSec").text))) + TS, "title": [(i.find("name").text, "")], "desc": [(i.find("shortDescription").text, "")]})
        sys.stdout.write('\x1b[1A')
        print(date_ + "  OK")
    print("\n")
    return channels, programmes


def get_o2_programmes(o2, d, d_b):
    channelKeys = o2.split(",")
    channels = []
    o2_idd = []
    for x in channelKeys:
        o2_idd.append(x.replace(" HD", "").replace("Eurosport3", "Eurosport 3").replace("Eurosport4", "Eurosport 4").replace("Eurosport5", "Eurosport 5"))
    c = {"display-name": [(replace_names("O2TV Sport"), u"cs")], "id": "o2tv-sport", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}, {"display-name": [(replace_names("O2TV Fotbal"), u"cs")], "id": "o2tv-fotbal", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-tv-fotbal.png'}]}, {"display-name": [(replace_names("O2TV Tenis"), u"cs")], "id": "o2tv-tenis", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-tv-tenis.png'}]}, {"display-name": [(replace_names("O2TV Sport1"), u"cs")], "id": "o2tv-sport1", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}, {"display-name": [(replace_names("O2TV Sport2"), u"cs")], "id": "o2tv-sport2", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}, {"display-name": [(replace_names("O2TV Sport3"), u"cs")], "id": "o2tv-sport3", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}, {"display-name": [(replace_names("O2TV Sport4"), u"cs")], "id": "o2tv-sport4", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}, {"display-name": [(replace_names("O2TV Sport5"), u"cs")], "id": "o2tv-sport5", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}, {"display-name": [(replace_names("O2TV Sport6"), u"cs")], "id": "o2tv-sport6", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}, {"display-name": [(replace_names("O2TV Sport7"), u"cs")], "id": "o2tv-sport7", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}, {"display-name": [(replace_names("O2TV Sport8"), u"cs")], "id": "o2tv-sport8", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/o2-sport-hd.png'}]}, {"display-name": [(replace_names("Eurosport 3"), u"cs")], "id": "eurosport-3", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/eurosport-3.png'}]}, {"display-name": [(replace_names("Eurosport 4"), u"cs")], "id": "eurosport-4", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/eurosport-4.png'}]}, {"display-name": [(replace_names("Eurosport 5"), u"cs")], "id": "eurosport-5", "icon": [{"src": 'https://assets.o2tv.cz/assets/images/tv-logos/original/eurosport-5.png'}]}
    for x in c:
        if x["display-name"][0][0].replace("O2TV", "O2") in o2_idd:
            channels.append(x)
    params = ""
    for channelKey in channelKeys:
        params = params + ("&channelKey=" + quote(channelKey))
    programmes = []
    for i in range(int(d_b)*-1, int(d)):
        next_day = datetime.combine(date.today(), datetime.min.time()) + timedelta(days = i)
        date_ = next_day.strftime("%d.%m.%Y")
        to_day = next_day  + timedelta(minutes = 1439)
   
