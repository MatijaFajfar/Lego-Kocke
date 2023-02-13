import csv
import json
import os
import requests
import sys
import re


def pripravi_imenik(ime_datoteke):
    '''Če še ne obstaja, pripravi prazen imenik za dano datoteko.'''
    imenik = os.path.dirname(ime_datoteke)
    if imenik:
        os.makedirs(imenik, exist_ok=True)


def shrani_spletno_stran(url, ime_datoteke, vsili_prenos=False):
    '''Vsebino strani na danem naslovu shrani v datoteko z danim imenom.'''
    try:
        print(f'Shranjujem {url} ...', end='')
        sys.stdout.flush()
        if os.path.isfile(ime_datoteke) and not vsili_prenos:
            print('shranjeno že od prej!')
            return
        r = requests.get(url)
    except requests.exceptions.ConnectionError:
        print('stran ne obstaja!')
    else:
        pripravi_imenik(ime_datoteke)
        with open(ime_datoteke, 'w', encoding='utf-8') as datoteka:
            datoteka.write(r.text)
            print('shranjeno!')


def vsebina_datoteke(ime_datoteke):
    '''Vrne niz z vsebino datoteke z danim imenom.'''
    with open(ime_datoteke, encoding='utf-8') as datoteka:
        return datoteka.read()


def zapisi_csv(slovarji, imena_polj, ime_datoteke):
    '''Iz seznama slovarjev ustvari CSV datoteko z glavo.'''
    pripravi_imenik(ime_datoteke)
    with open(ime_datoteke, 'w', encoding='utf-8') as csv_datoteka:
        writer = csv.DictWriter(csv_datoteka, fieldnames=imena_polj)
        writer.writeheader()
        writer.writerows(slovarji)


def zapisi_json(objekt, ime_datoteke):
    '''Iz danega objekta ustvari JSON datoteko.'''
    pripravi_imenik(ime_datoteke)
    with open(ime_datoteke, 'w', encoding='utf-8') as json_datoteka:
        json.dump(objekt, json_datoteka, indent=4, ensure_ascii=False)

skupni_vzorec = re.compile(
    r"title=\"(?P<id>.*?): (?P<Naslov>.*?)\" onError.*?"
    r"<a href='\/sets\/theme-(?P<tema>.*?)'>.*?"
    r"(.*?<a class='subtheme' href='/sets/subtheme.*?'>(?P<podtema>.*?)</a>)?"
    r"(.*?Our community</dt><dd class='hideingallery'>(?P<podatki_o_skupnosti>.*?)</dd>)?"
    r"(.*?class='half'>&#10029;</span>(?P<ocena>.+?)</span>)?"
    r"(.*?href='ratings\?set=.*'>(?P<st_ocen>\d*) ratings</a>)?"
    r"(.*?<dt>Pieces</dt><dd><a class='plain' href='/inventories/.+?'>(?P<st_delov>\d*)</a></dd>)?"
    r"(.*?<dt>Minifigs</dt><dd><a class='plain' href='/minifigs/in-.*?'>(?P<figure>.*?)</dd>)?"
    r"(.*?</dd><dt>RRP</dt><dd>\$?.*? (?P<cena>.*?)€? \| <a class=)?"
    r"(.*?<dt>PPP</dt><dd>.*?c?, (?P<cena_glede_na_kos>.*?)c</dd>)?"
    r"(.*?<dt>Packaging</dt><dd>(?P<pakiranje>.*?)</dd>)?"
    r"(.*?<dt>Availability</dt><dd>(?P<dostopnost>.*?)</dd>)?"
    r"(.*?<dt>Set type</dt><dd>(?P<tip_seta>.*?)</dd>)?"
    r"(.*?<dt>Designer</dt><dd class='tags'><a href='/sets/designer-.*?'>(?P<oblikovalec>.*?)</a>)?"
    ,
    flags=re.DOTALL
)