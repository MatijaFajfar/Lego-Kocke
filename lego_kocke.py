import stevila_setov_po_letih as leta
import csv
import os
import requests
import re
import time
import random
import math
import json

kocke = []


brickset_glavni_url = 'https://brickset.com/sets/year-'

strani = 'strani'


def download_url_to_string(url):
    """Funkcija kot argument sprejme niz in poskusi vrniti vsebino te spletne
    strani kot niz. V primeru, da med izvajanje pride do napake vrne None.
    """
    try:
        page_content = requests.get(url).text
    except Exception as e:
        print(f'Prišlo je do napake pri prenosu: {url} ::!', e)
        return None
    return page_content


def save_string_to_file(text, directory, filename):
    """Funkcija zapiše vrednost parametra "text" v novo ustvarjeno datoteko
    locirano v "directory"/"filename", ali povozi obstoječo. V primeru, da je
    niz "directory" prazen datoteko ustvari v trenutni mapi.
    """
    os.makedirs(directory, exist_ok=True)
    path = os.path.join(directory, filename)
    with open(path, 'w', encoding='utf-8') as file_out:
        file_out.write(text)
    return None



def save_frontpage(page, directory, filename):
    """Funkcija shrani vsebino spletne strani na naslovu "page" v datoteko
    "directory"/"filename"."""
    tekst = download_url_to_string(page)
    save_string_to_file(tekst, directory, filename)
    print('Stran shranjena')

def random_stevilo_sekund():
    return random.randint(1, 4)

def shrani_strani(seznam_strani):
    for (leto, letno_stevilo_setov) in seznam_strani:
        stevilo_strani = math.ceil(letno_stevilo_setov / 25)
        for stran in range(1, stevilo_strani + 1):
            url = brickset_glavni_url + f"{leto}/page-{stran}"
            save_frontpage(url, 'LEGO_KOCKE', f"{leto}_stran_{stran}")
            time.sleep(random_stevilo_sekund())

#shrani_strani(leta.leta)

def read_file_to_string(directory, filename):
    """Funkcija vrne celotno vsebino datoteke "directory"/"filename" kot niz."""
    path = os.path.join(directory, filename)
    with open(path, encoding='utf-8') as datoteka:
        return datoteka.read()

vzorec_bloka = r"<article class='set'.*?<\/article>"

def najdi_bloke(page_content):
    bloki = re.findall(vzorec_bloka, page_content, re.DOTALL | re.IGNORECASE)
    return bloki

vzorec_kompleta = re.compile(
    r"title=\"(?P<id>.*?): (?P<Naslov>.*?)\" onError.*?"
    r"<a href='\/sets\/theme-(?P<tema>.*?)'>.*?"
    ,flags=re.DOTALL)

vzorec_podteme = re.compile(r"<a class='subtheme' href='\/sets\/subtheme.*?'>(?P<podtema>.*?)<\/a>",flags=re.DOTALL)
vzorec_za_tip_seta = re.compile(r"<dt>Set type<\/dt><dd>(?P<tip_seta>.*?)<\/dd>",flags=re.DOTALL)
vzorec_za_podatke_o_skupnosti = re.compile(r"Our community<\/dt><dd class='hideingallery'>(?P<podatki_o_skupnosti>.*?)<\/dd>",flags=re.DOTALL)

vzorec_ocene = re.compile(r"class='half'>&#10029;<\/span>(?P<ocena>.+?)<\/span>",flags=re.DOTALL)
vzorec_števila_ocen = re.compile(r"href='ratings\?set=.*'>(?P<st_ocen>\d*) ratings<\/a>",flags=re.DOTALL)
vzorec_števila_delov = re.compile(r"<dt>Pieces<\/dt><dd><a class='plain' href='\/inventories\/.+?'>(?P<st_delov>\d*)<\/a><\/dd>",flags=re.DOTALL)
vzorec_za_stevilo_figuric = re.compile(r"<dt>Minifigs<\/dt><dd><a class='plain' href='\/minifigs\/in-.*?'>(?P<figure>.*?)<\/dd>",flags=re.DOTALL)
vzorec_za_ceno = re.compile(r"<\/dd><dt>RRP<\/dt><dd>\$?.*? (?P<cena>.*?)€? \| <a class=",flags=re.DOTALL)
vzorec_za_ceno_glede_na_kos = re.compile(r"<dt>PPP<\/dt><dd>.*?c?, (?P<cena_glede_na_kos>.*?)c<\/dd>",flags=re.DOTALL)
vzorec_za_pakiranje = re.compile(r"<dt>Packaging<\/dt><dd>(?P<pakiranje>.*?)<\/dd>",flags=re.DOTALL)
vzorec_za_dostopnost = re.compile(r"<dt>Availability<\/dt><dd>(?P<dostopnost>.*?)<\/dd>",flags=re.DOTALL)
vzorec_za_oblikovalca = re.compile(r"<dt>Designer<\/dt><dd class='tags'><a href='\/sets\/designer-.*?'>(?P<oblikovalec>.*?)<\/a>",flags=re.DOTALL)

vzorec_zelijo_komplet = re.compile(r"(?P<zelijo>\d+) want")
vzorec_imajo_komplet = re.compile(r"(?P<imajo>\d+) own")
vzorec_vse_figure = re.compile(r"(?P<vse>\d+?)<\/a>")
vzorec_unikatne_figure = re.compile(r"(?P<unikatne>\d+?) Unique")

vzorci = [
    (vzorec_podteme, "podtema"),
    (vzorec_za_tip_seta, "tip_seta"),
    (vzorec_ocene, "ocena"),
    (vzorec_števila_ocen, "st_ocen"),
    (vzorec_števila_delov, "st_delov"),
    (vzorec_za_ceno, "cena"),
    (vzorec_za_ceno_glede_na_kos, "cena_glede_na_kos"),
    (vzorec_za_pakiranje, "pakiranje"),
    (vzorec_za_dostopnost, "dostopnost"),
    (vzorec_za_oblikovalca, "oblikovalec")
]

def izlusci_podatke_iz_bloka(blok, leto):
    komplet = vzorec_kompleta.search(blok).groupdict()
    for (vzorec, lastnost) in vzorci:
        vrednost = vzorec.search(blok)
        if vrednost:
            komplet[lastnost] = vrednost[lastnost]
        else:
            komplet[lastnost] = None
    skupnost = vzorec_za_podatke_o_skupnosti.search(blok)
    if skupnost:
        zelijo = vzorec_zelijo_komplet.search(skupnost['podatki_o_skupnosti'])
        imajo = vzorec_imajo_komplet.search(skupnost['podatki_o_skupnosti'])
        if zelijo:
            komplet['Želijo komplet'] = zelijo['zelijo']
        else:
            komplet['Želijo komplet'] = None
        if imajo:
            komplet['Imajo komplet'] = imajo['imajo']
        else:
            komplet['Imajo komplet'] = None
    figure = vzorec_za_stevilo_figuric.search(blok)
    if figure:
        vse = vzorec_vse_figure.search(figure['figure'])
        unikatne = vzorec_unikatne_figure.search(figure['figure'])
        if vse:
            komplet['Vse Minifigure'] = vse['vse']
        else: 
            komplet['Vse Minifigure'] = None
        if unikatne:
            komplet['Unikatne Minifigure'] = unikatne['unikatne']
        else:
            komplet['Unikatne Minifigure'] = None
    komplet['Leto izdaje'] = leto
    return komplet

def izlusci_iz_strani(directory, filename, leto):
    stran = read_file_to_string(directory, filename)
    bloki = najdi_bloke(stran)
    for blok in bloki:
        podatki = izlusci_podatke_iz_bloka(blok, leto)
        kocke.append(podatki)
        print('Blok Izluščen')


#izlusci_iz_strani('LEGO_KOCKE','2022_stran_1')


def pripravi_imenik(ime_datoteke):
    '''Če še ne obstaja, pripravi prazen imenik za dano datoteko.'''
    imenik = os.path.dirname(ime_datoteke)
    if imenik:
        os.makedirs(imenik, exist_ok=True)

def zapisi_csv(slovarji, imena_polj, ime_datoteke):
    '''Iz seznama slovarjev ustvari CSV datoteko z glavo.'''
    pripravi_imenik(ime_datoteke)
    with open(ime_datoteke, 'w', encoding='utf-8') as csv_datoteka:
        writer = csv.DictWriter(csv_datoteka, fieldnames=imena_polj)
        writer.writeheader()
        writer.writerows(slovarji)



#for (leto, letno_stevilo_setov) in leta.leta:
#        stevilo_strani = math.ceil(letno_stevilo_setov / 25)
#        for stran in range(1, stevilo_strani + 1):
#            izlusci_iz_strani('LEGO_KOCKE',f'{leto}_stran_{stran}', leto)
#zapisi_csv(
#    kocke,
#    ["id","Naslov","tema","podtema","tip_seta","ocena","st_ocen","st_delov","cena","cena_glede_na_kos","pakiranje","dostopnost","oblikovalec","Želijo komplet","Imajo komplet","Vse Minifigure",'Unikatne Minifigure',"Leto izdaje"],
#        'obdelani-podatki/kompleti.csv'
#)

#koda, ki je iz csv datoteke odstranila prazne vrstice
#with open('kompleti.csv', newline='', encoding='utf8') as in_file:
#    with open('neurejeni_podatki.csv', 'w', newline='', encoding='utf8') as out_file:
#        writer = csv.writer('kompleti.csv')
#        for row in csv.reader('neurejeni_podatki.csv'):
#            if row:
#                writer.writerow(row)