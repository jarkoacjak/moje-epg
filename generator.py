import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

OUTPUT_FILE = "epg-cz.xml"
MY_CHANNEL_ID = "MarkizaKlasik.sk"
MY_CHANNEL_NAME = "Markíza Klasik"
LOGO_URL = "https://img.vsetkynasvete.sk/markiza-klasik-logo.png"

def scrape_tv_program_sk():
    print("Sťahujem program priamo z tv-program.sk...")
    url = "https://www.tv-program.sk/stanica/markiza-klasik"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Vytvorenie koreňového XML elementu <tv>
        tv = ET.Element("tv", {"generator-info-name": "TVProgramSkScraperOnly"})
        
        # Pridanie kanálu <channel>
        channel = ET.SubElement(tv, "channel", id=MY_CHANNEL_ID)
        display_name = ET.SubElement(channel, "display-name", lang="sk")
        display_name.text = MY_CHANNEL_NAME
        ET.SubElement(channel, "icon", src=LOGO_URL)
        
        # Nájdeme všetky stĺpce dní (Streda, Štvrtok, Piatok...)
        # Na webe bývajú označené triedami pre stĺpce
        dni_bloky = soup.find_all(class_="station-program-col") or soup.find_all(class_="program-col")
        
        # Ak nenašiel stĺpce, prehľadáme celú stránku naraz
        if not dni_bloky:
            dni_bloky = [soup]
            
        base_date = datetime.now()
        count = 0
        
        for idx, blok in enumerate(dni_bloky[:3]):  # Spracujeme max 3 dni dopredu
            target_date = base_date + timedelta(days=idx)
            date_str = target_date.strftime("%Y%m%d")
            
            # Nájdeme riadky s reláciami
            rows = blok.select(".program-row, .row, li, tr")
            
            for row in rows:
                # 1. Hľadáme čas (napr. 06:00)
                time_el = row.find(class_="time") or row.find(class_="cas")
                if not time_el:
                    # Ak nemá class, skúsim nájsť akýkoľvek text s dvojbodkou, čo vyzerá ako čas
                    for span in row.find_all(["span", "div"]):
                        text = span.text.strip()
                        if ":" in text and len(text) == 5 and text.replace(":", "").isdigit():
                            time_el = span
                            break
                
                # 2. Hľadáme názov relácie (napr. Alf)
                title_el = row.find(class_="title") or row.find(class_="nazov") or row.find("a")
                
                if time_el and title_el:
                    time_raw = time_el.text.strip().replace(":", "")  # "06:00" -> "0600"
                    title_raw = title_el.text.strip()
                    
                    if len(time_raw) == 4 and time_raw.isdigit() and title_raw:
                        start_time = f"{date_str}{time_raw}00 +0200"
                        
                        # Orientačný koniec o hodinu neskôr (IPTV prehrávače si to zarovnajú podľa štartu ďalšej)
                        stop_time = f"{date_str}{str(int(time_raw)+100).zfill(4)}00 +0200"
                        
                        programme = ET.SubElement(tv, "programme", start=start_time, stop=stop_time, channel=MY_CHANNEL_ID)
                        t = ET.SubElement(programme, "title", lang="sk")
                        t.text = title_raw
                        
                        count += 1

        if count == 0:
            print("Zlyhalo automatické parsovanie. Skontroluj, či sa nezmenil kód stránky.")
            return

        # Uloženie do súboru s pekným odsadením
        tree = ET.ElementTree(tv)
        ET.indent(tree, space="  ", level=0)
        
        with open(OUTPUT_FILE, "wb") as f:
            f.write(b'<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write(b'<!DOCTYPE tv SYSTEM "xmltv.dtd">\n')
            tree.write(f, encoding="utf-8", xml_declaration=False)
            
        print(f"Úspešne dokončené! Súbor {OUTPUT_FILE} bol vytvorený a obsahuje {count} relácií z tv-program.sk.")
        
    except Exception as e:
        print(f"Chyba pri sťahovaní: {e}")

if __name__ == "__main__":
    scrape_tv_program_sk()


