import datetime
import xml.etree.ElementTree as ET
from xml.dom import minidom
import requests
from bs4 import BeautifulSoup

# Nastavenie hlavičiek, aby nás web neblokoval
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Zoznam staníc a ich URL adries z tvojich screenshotov
STANCE_LINKS = {
    "MarkizaKlasik.sk": "https://telkac.zoznam.sk/tv-program-stanice/227/markiza-klasik",
    "JOJSport.sk": "https://tv-program.aktuality.sk/stanica/joj-sport/",
    "JOJSport2.sk": "https://tv-program.aktuality.sk/stanica/joj-sport-2/",
}


def vytvor_epg():
    # Inicializácia XML štruktúry
    root = ET.Element("tv", {"generator-info-name": "JarkoAcjak Auto EPG"})

    # Vytvorenie definície kanálov
    for channel_id, _ in STANCE_LINKS.items():
        channel_el = ET.SubElement(root, "channel", id=channel_id)
        display_name = ET.SubElement(channel_el, "display-name")
        display_name.text = channel_id.replace(".sk", "").replace(
            "Markiza", "Markíza"
        )

    Dnes = datetime.date.today()

    for channel_id, url in STANCE_LINKS.items():
        print(f"Sťahujem program pre: {channel_id}...")
        try:
            response = requests.get(url, headers=HEADERS)
            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.content, "html.parser")

            # 1. PARSOVANIE PRE TELKÁČ (Markíza Klasik)
            if "telkac.zoznam.sk" in url:
                # Skript nájde riadky s reláciami
                for row in soup.select(".station-program-row"):
                    cas_text = (
                        row.select_one(".time").text.strip()
                        if row.select_one(".time")
                        else ""
                    )
                    titulok = (
                        row.select_one(".title").text.strip()
                        if row.select_one(".title")
                        else ""
                    )

                    if cas_text and titulok:
                        hod, mnt = map(int, cas_text.split(":"))
                        # Zápis času do XML formátu (napr. 20260625180000 +0200)
                        start_cas = f"{dnes.strftime('%Y%m%d')}{hod:02d}{mnt:02d}00 +0200"

                        programme_el = ET.SubElement(
                            root,
                            "programme",
                            start=start_cas,
                            channel=channel_id,
                        )
                        title_el = ET.SubElement(programme_el, "title", lang="sk")
                        title_el.text = titulok

            # 2. PARSOVANIE PRE AKTUALITY (JOJ Šport 1 a 2)
            elif "aktuality.sk" in url:
                for row in soup.select(".tv-program-items .item"):
                    cas_text = (
                        row.select_one(".time").text.strip()
                        if row.select_one(".time")
                        else ""
                    )
                    titulok = (
                        row.select_one(".title").text.strip()
                        if row.select_one(".title")
                        else ""
                    )

                    if cas_text and titulok:
                        hod, mnt = map(int, cas_text.split(":"))
                        start_cas = f"{dnes.strftime('%Y%m%d')}{hod:02d}{mnt:02d}00 +0200"

                        programme_el = ET.SubElement(
                            root,
                            "programme",
                            start=start_cas,
                            channel=channel_id,
                        )
                        title_el = ET.SubElement(programme_el, "title", lang="sk")
                        title_el.text = titulok

        except Exception as e:
            print(f"Chyba pri sťahovaní {channel_id}: {e}")

    # Uloženie do pekného naformátovaného XML súboru
    xml_str = ET.tostring(root, encoding="utf-8")
    parsed_xml = minidom.parseString(xml_str)
    pretty_xml = parsed_xml.toprettyxml(indent="  ", encoding="utf-8")

    with open("epg.xml", "wb") as f:
        f.write(pretty_xml)
    print("Súbor epg.xml bol úspešne vygenerovaný!")


if __name__ == "__main__":
    vytvor_epg()


