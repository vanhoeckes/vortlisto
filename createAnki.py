import genanki
import pickle
from os import listdir, mkdir
from os.path import join
from random import randrange

##ANKI ID's
def genID():
    return randrange(1 << 30, 1 << 31)

def getIDs(IDs, CSV):
    if IDs in listdir("."):
        f = open(IDs,'rb')
        ANKI_IDS = pickle.load(f)
        f.close()
    else:
        ANKI_IDS = {"model" : genID(), 
                    "basic": genID(), 
                    "advanced": genID()}

    for dosiero in listdir(CSV):
        (bloko, etendajo) = tuple(dosiero.split("."))
        (temo, nivelo) = tuple(bloko.split("-"))
        if not temo in ANKI_IDS.keys():
            ANKI_IDS[temo] = genID()

    f = open(IDs, "wb")
    pickle.dump(ANKI_IDS, f)
    f.close()
    
    return ANKI_IDS

#ANKI Modelo
def getModelo(ANKI_IDS):
    modelo = genanki.Model(
        ANKI_IDS["model"],
        "Modelo",
        fields=[
            {'name':'vorto'},
            {'name':'word'}
        ],
        templates = [
            {
                'name'  : 'vorto@word',
                'qfmt'  : '{{vorto}}',
                'afmt'  : '{{FrontSide}}<hr id="answer">{{word}}',
            },
            {
                'name'  : 'word@vorto',
                'qfmt'  : '{{word}}',
                'afmt'  : '{{FrontSide}}<hr id="answer">{{vorto}}',
            }  
        ]
    )
    return modelo

#ANKI Stako
def beligi(temo):
    return "Esperanto::%s" % (temo.replace("_"," ").title() )

def getStakoj(ANKI_IDS):
    STAKOJ = {}
    for slosilo, id in ANKI_IDS.items():
        if slosilo == "model":
            continue
        STAKOJ[slosilo] = genanki.Deck(id ,beligi(slosilo))
    return STAKOJ

#ANKI Walk CSV
def walkCSV(CSV, STAKOJ, modelo):
    for dosiero in listdir(CSV):
        (bloko, etendajo) = tuple(dosiero.split("."))
        (temo, nivelo) = tuple(bloko.split("-"))
        f = open(join(CSV,dosiero),'r')
        txt = f.read()
        f.close()

        for linio in txt.split('\n'):
            if len(linio) < 1:
                continue 
            segmentoj  = linio.split(",",1)
            segmentoj[1] = segmentoj[1].strip('"')
            noto = genanki.Note(
                model   = modelo,
                fields  = segmentoj,
                tags    = [temo, nivelo]
            )
            STAKOJ[nivelo].add_note(noto)
            STAKOJ[temo].add_note(noto)
    return STAKOJ

#ANKI Generate Packs
def genPakoj(STAKOJ, ANKI):
    if not ANKI in listdir('.'):
        mkdir(ANKI)
    for slosilo, stako in STAKOJ.items():
        pack = genanki.Package(stako)
        pack.write_to_file(join(ANKI, "%s.apkg" % slosilo))

#MAIN
def main():
    CSV      = "csv"
    ANKI     = "anki"
    IDs      = "IDs.log"
    ANKI_IDS = getIDs(IDs, CSV)
    MODELO   = getModelo(ANKI_IDS)
    STAKOJ   = getStakoj(ANKI_IDS)
    STAKOJ   = walkCSV(CSV, STAKOJ, MODELO)
    genPakoj(STAKOJ, ANKI)

if __name__ == "__main__":
    main()
