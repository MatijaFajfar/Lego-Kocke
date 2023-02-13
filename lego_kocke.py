import csv
import os
import requests
import re
import time
import random
import orodja

kocke = []
leta = range(1949, 2023)

brickset_glavni_url = 'https://brickset.com/sets/year-'
cookies_dict = {'setsPageLength': "1000"} # Cookie omogoča, da za vsako leto naložimo le eno stran


def download_url_to_string(url):
    """Funkcija kot argument sprejme niz in poskusi vrniti vsebino te spletne
    strani kot niz. V primeru, da med izvajanje pride do napake vrne None.
    """
    try:
        page_content = requests.get(url, cookies=cookies_dict).text
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


def shrani_strani(seznam_strani):
    for leto in seznam_strani:
        url = brickset_glavni_url + f"{leto}"
        save_frontpage(url, 'BRICKSET_STRANI', f"kompleti_{leto}")
        time.sleep(random.randint(1, 4))

#shrani_strani(leta)

def read_file_to_string(directory, filename):
    """Funkcija vrne celotno vsebino datoteke "directory"/"filename" kot niz."""
    path = os.path.join(directory, filename)
    with open(path, encoding='utf-8') as datoteka:
        return datoteka.read()

vzorec_bloka = r"<article class='set'>.*?<\/article>"

def najdi_bloke(page_content):
    bloki = re.findall(vzorec_bloka, page_content, re.DOTALL | re.IGNORECASE)
    return bloki

vzorec_kompleta = re.compile(
    r"title=\"(?P<Id>.*?): (?P<Naslov>.*?)\" onError.*?"
    r"<a href='\/sets\/theme-(?P<Tema>.*?)'>.*?"
    ,flags=re.DOTALL)

vzorec_podteme = re.compile(r"<a class='subtheme' href='\/sets\/subtheme.*?'>(?P<Podtema>.*?)<\/a>",flags=re.DOTALL)
vzorec_za_tip_seta = re.compile(r"<dt>Set type<\/dt><dd>(?P<Tip_seta>.*?)<\/dd>",flags=re.DOTALL)
vzorec_za_podatke_o_skupnosti = re.compile(r"Our community<\/dt><dd class='hideingallery'>(?P<Podatki_o_skupnosti>.*?)<\/dd>",flags=re.DOTALL)

vzorec_ocene = re.compile(r"<\/span>(?P<Ocena> \d.\d)<\/span>", flags=re.DOTALL)
vzorec_števila_ocen = re.compile(r"href='ratings\?set=.*'>(?P<Št_ocen>\d*) ratings<\/a>", flags=re.DOTALL)
vzorec_števila_delov = re.compile(r"<dt>Pieces<\/dt><dd><a class='plain' href='\/inventories\/.+?'>(?P<Št_delov>\d*)<\/a><\/dd>", flags=re.DOTALL)
vzorec_za_stevilo_figuric = re.compile(r"<dt>Minifigs<\/dt><dd><a class='plain' href='\/minifigs\/in-.*?'>(?P<Figure>.*?)<\/dd>", flags=re.DOTALL)
vzorec_za_ceno = re.compile(r"<\/dd><dt>RRP<\/dt><dd>\$?.*? (?P<Cena>.*?)€? \| <a class=", flags=re.DOTALL)
vzorec_za_ceno_glede_na_kos = re.compile(r"<dt>PPP<\/dt><dd>.*?c?, (?P<Cena_glede_na_kos>.*?)c<\/dd>", flags=re.DOTALL)
vzorec_za_pakiranje = re.compile(r"<dt>Packaging<\/dt><dd>(?P<Pakiranje>.*?)<\/dd>", flags=re.DOTALL)
vzorec_za_dostopnost = re.compile(r"<dt>Availability<\/dt><dd>(?P<Dostopnost>.*?)<\/dd>", flags=re.DOTALL)
vzorec_za_oblikovalca = re.compile(r"<dt>Designer<\/dt><dd class='tags'><a href='\/sets\/designer-.*?'>(?P<Oblikovalec>.*?)<\/a>", flags=re.DOTALL)
vzorec_zelijo_komplet = re.compile(r"(?P<Zelijo>\d+) want", flags=re.DOTALL)
vzorec_imajo_komplet = re.compile(r"(?P<Imajo>\d+) own", flags=re.DOTALL)
vzorec_vse_figure = re.compile(r"(?P<Vse>\d+?)<\/a>", flags=re.DOTALL)
vzorec_unikatne_figure = re.compile(r"(?P<Unikatne>\d+?) Unique", flags=re.DOTALL)

vzorci = [
    (vzorec_podteme, "Podtema"),
    (vzorec_za_tip_seta, "Tip_seta"),
    (vzorec_ocene, "Ocena"),
    (vzorec_števila_ocen, "Št_ocen"),
    (vzorec_števila_delov, "Št_delov"),
    (vzorec_za_ceno, "Cena"),
    (vzorec_za_ceno_glede_na_kos, "Cena_glede_na_kos"),
    (vzorec_za_pakiranje, "Pakiranje"),
    (vzorec_za_dostopnost, "Dostopnost"),
    (vzorec_za_oblikovalca, "Oblikovalec")
]

def izlusci_podatke_iz_bloka(blok, leto):
    # En sam večji regex bi najverjetneje bil bolj učinkovit, a je na strani občasno vrstni red podatkov drugačen in tak regex ne bi našel vseh podatkov.
    komplet = vzorec_kompleta.search(blok).groupdict()
    for (vzorec, lastnost) in vzorci:
        vrednost = vzorec.search(blok)
        if vrednost:
            komplet[lastnost] = vrednost[lastnost]
        else:
            komplet[lastnost] = None
    skupnost = vzorec_za_podatke_o_skupnosti.search(blok)
    if skupnost:
        zelijo = vzorec_zelijo_komplet.search(skupnost['Podatki_o_skupnosti'])
        imajo = vzorec_imajo_komplet.search(skupnost['Podatki_o_skupnosti'])
        if zelijo:
            komplet['Želijo_komplet'] = zelijo['Zelijo']
        else:
            komplet['Želijo_komplet'] = 0
        if imajo:
            komplet['Imajo_komplet'] = imajo['Imajo']
        else:
            komplet['Imajo_komplet'] = 0
    figure = vzorec_za_stevilo_figuric.search(blok)
    if figure:
        vse = vzorec_vse_figure.search(figure['Figure'])
        unikatne = vzorec_unikatne_figure.search(figure['Figure'])
        if vse:
            komplet['Vse_Minifigure'] = vse['Vse']
        else: 
            komplet['Vse_Minifigure'] = 0
        if unikatne:
            komplet['Unikatne_Minifigure'] = unikatne['Unikatne']
        else:
            komplet['Unikatne_Minifigure'] = 0
    komplet['Leto_izdaje'] = leto
    return komplet

def izlusci_iz_strani(directory, filename, leto):
    stran = read_file_to_string(directory, filename)
    bloki = najdi_bloke(stran)
    for blok in bloki:
        podatki = izlusci_podatke_iz_bloka(blok, leto)
        kocke.append(podatki)
        print('Blok Izluščen')

#izlusci_iz_strani('BRICKSET_STRANI', 'kompleti_2022', 2022)

#print(izlusci_iz_strani('BRICKSET_STRANI', 'kompleti_2022', 2022))

for leto in leta:
    izlusci_iz_strani('BRICKSET_STRANI',f'kompleti_{leto}', leto)
orodja.zapisi_csv(
    kocke,
    ["Id","Naslov","Tema","Podtema","Tip_seta","Ocena","Št_ocen","Št_delov","Cena","Cena_glede_na_kos","Pakiranje","Dostopnost","Želijo_komplet","Imajo_komplet","Vse_Minifigure",'Unikatne_Minifigure',"Leto_izdaje", "Oblikovalec"],
    'obdelani-podatki/kompleti.csv'
)

#koda, ki je iz csv datoteke odstranila prazne vrstice
with open('obdelani-podatki/kompleti.csv', newline='', encoding='utf8') as in_file:
    with open('podatki.csv', 'w', newline='', encoding='utf8') as out_file:
        writer = csv.writer(out_file)
        for row in csv.reader(in_file):
            if row:
                writer.writerow(row)