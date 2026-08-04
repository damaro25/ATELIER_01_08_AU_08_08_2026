# -*- coding: utf-8 -*-
"""
Script d'attribution automatique du sexe (P03) à partir du prénom (P01XA)
pour les données du RGPH4 Guinée.

PRINCIPE
--------
1. On dispose d'un dictionnaire de prénoms/racines courants en Guinée
   (peul, malinké, soussou, kissi, guerzé/toma + prénoms chrétiens),
   classés Homme / Femme.
2. Pour les prénoms composés (ex: "MAMADOU ALIOU", "FATOUMATA BINTA"),
   le premier mot porte en général le genre en Guinée -> on teste
   d'abord le nom complet, puis le premier mot.
3. Tout prénom non reconnu est laissé à blanc (manquant) et flaggé
   "A_VERIFIER" pour un contrôle manuel plutôt que de deviner au hasard
   -> c'est le choix le plus sûr pour des données de recensement.

UTILISATION
-----------
    python attribuer_sexe_prenoms.py input.xlsx output.xlsx

- input.xlsx doit contenir une colonne "P01XA" (prénom).
- Si aucun fichier n'est fourni, le script utilise la liste collée par
  l'utilisateur (fonction demo()) et écrit un fichier de démonstration.

Le fichier de sortie contient :
    P01XA | P03 | P03_LABEL | A_VERIFIER
avec P03 codé 1 = Homme, 2 = Femme, et P03 laissé vide si non reconnu.
"""

import sys
import re
import unicodedata
import pandas as pd

# ---------------------------------------------------------------------
# 1. DICTIONNAIRE DE PRENOMS / RACINES GUINEENNES
#    (à enrichir librement : c'est une simple liste Python)
# ---------------------------------------------------------------------

HOMMES = [
    "MOUSSA", "SEYOU", "DJIBRIL", "ABDOUL AZIZ", "ABDOUL", "ABOU", "SEKOU",
    "IBRAHIM", "IBRAHIMA", "ISIAKA", "KARAMO", "KARAMOKO", "ABOUBACAR",
    "ABOUBAKAR", "MAMOUDOU", "MAMADOU", "MAMADI", "MAMADY", "MAMADOUBA",
    "SAYON", "ABDOULAYE", "ADOULAYE", "LANCINET", "LANCINE", "LANCINÈ",
    "LANCE", "LANCEI", "LAYE", "MOHAMED", "MOHAMEDE", "MOHAMED LAMINE",
    "MOHAED", "MONHAMED", "AMADOU", "HAROUNA", "YAYA", "YOUSSOUF",
    "YSSOUFOU", "YAMOUSSA", "ALHOUSSENY", "SOULEYMANE", "SOULYMANE",
    "SEULEMANE", "OUSMANI", "OUSMANE", "SOUAIBOU", "NOUHAN", "KARIFA",
    "SIDIKI", "SIDIBA", "ABBAS", "ZAKARIA", "KEMO", "KEM", "ALY", "ALI",
    "ALIOU", "LASSO", "DEMBA", "ISSIFOU", "KASSIMOU", "OUMAR", "ALSEINY",
    "ALSENY", "ALHASSANE", "ALAHSANE", "ISSAGHA", "BAKARI", "BAKARY",
    "LADJI", "HAMIDOU", "FODE", "FODÉ", "MORY", "MORIBA", "SORI", "SORY",
    "SÉKOU", "NFALI", "NFALY", "N'FALY", "SIAKA", "BANGALY", "MARC",
    "SAIDOU", "SAIDOUBA", "BENOIT", "ETIENNE", "ETHIENE", "IDRISSA",
    "IDI", "LOUIS", "PATRICE", "GEORGES", "MOÏSE", "MOISE", "CHRIST",
    "BOURAMA", "DJIBA", "TAMBA", "BILLO", "ALPHA", "MORLAY", "MORLAYE",
    "MOMODOUBA", "ISSA", "ISMAEL", "ISMAËL", "ANSOUMANE", "DENIS",
    "SEK", "FACELY", "ABDOURAHMANE", "BREMA", "BRÉMA", "LAMINE",
    "SALIF", "DAOUDA", "SORIBA", "NABA", "GBO", "KONAN", "BLAISE",
    "REMY", "LAZARD", "NABY", "BAL", "LUC", "ALEXANDRE", "PHILIPE",
    "PHILIPPE", "ALASSANE", "MALICK", "KALILOU", "MACIRE", "KABINET",
    "VIEUX", "LASSINE", "BALLA", "KADIALY", "FAMAKAN", "DRAMANE",
    "KERFALA", "KEROUFALA", "ROBERT", "MICHEL", "ABOUDOU", "SOLO",
    "MARTIN", "BIENVENU", "THIERNO", "OUMAR DJOGO", "SANOUSSY",
    "KANFORY", "MOUCTAR", "MOUKTAR", "TIDIANE", "TIERNO", "ELHADJ",
    "EL HADJ", "ELLHADJ", "ALADJI", "COMMANDANT", "OUSSENI", "YOUNOUSSA",
    "KEROUANE", "SEKOUBA", "ZOUMANOU", "KALIL", "KALIFA", "AMARA",
    "MORY", "SIDIKI", "KEROU", "BALA", "MOHAMED ALPHA", "MOHAMED SEYDOU",
    "MOHAMED ALIOU", "PATRICE", "AUGUISTIN", "AUGUSTIN", "GONO",
    "JEAN", "JHP", "SIDIBE", "SACKO", "BAKARI", "SIA", "TAMBA KABA",
    "SIDIBA", "DJEBRIL", "SAA", "JOSEPH", "PAUL", "PIERRE", "PASCAL",
    "AMADOU DJOULDE", "AMADOU MALADHO", "AMADOU OURY", "AMADOU SAÏKOU",
    "AMADOU BAILO", "AMADOU BAÏLO", "AMADOU BAÏLLO", "AMADOU WOURI",
    "AMADOU TITIANE", "AMADOU SARA", "ALPHA OUMAR", "ALPHA SALIOU",
    "ALPHA OUSMANE", "ALPHA NOUW", "ELHADJ ALPHA OUMAR", "MOHAMED KOURIA",
    "MOHAMED MINA", "MOHAMED DJOBRIL", "MOHAMED AZIZ", "MOHAMED LAMARANA",
    "SEKOU OUMAR", "SEKOU2", "SEK", "OURY BAILO", "OURY BAILLO",
    "TAMBA MICHEL", "TAMBA KABA", "N'FAMOUSSA", "N'GOSSE",
    "MAMADOU FOULA", "MAMADOU ALIOU", "MAMADOU BACHIR", "MAMADOU SAMBA",
    "MAMADOU OURY", "MAMADOU SALIOU", "MAMADOU YAGOUBA", "MAMADOU KAALI",
    "MAMADOU DIAN", "MAMADOU YERO", "MAMADOU BOBO", "MAMADOU HADY",
    "MAMADOU LAMARANA", "MAMADOU MOUSSA", "MAMADOU FALILOU",
    "MAMADOU MALAL", "MAMADOU MALADHO", "MAMADOU ISSA", "MAMADOU BOUKARIOU",
    "MAMADOU DJOUDJA", "MAMADOU BAÏLO", "MAMADOU BAILLO",
    "MAMADOU MOUDJITABA", "MAMADOU MOUCTAR", "MAMADOU BOYE",
    "MAMADOU YAYA", "MAMADOU KALI", "MAMADOU DJOULDE", "MAMADOU BHOYE",
    "MAMADOU PURY", "MAMADOU BINTA", "MAMADOU MOUGNIR", "MAMADOUDJAN",
    "ELHADJ MAMADOU SALIO", "ELHADJ BOUBACAR", "ELHADJ SADOU",
    "ELHADJ OUMAR", "THIERNO SADOU", "THIERNO IBRAHIMA",
    "THIERNO ABDOULAYE", "THIERNO SOULEYMANE", "THIERNO OUMAR BAILO",
    "THIERNO ALHASSANE", "THIERNO IDRISSA", "THIERNO MOUSSA",
    "THIERNO AMADOU", "THIERNO BELLA", "THIERNO HASSANE",
    "THIERO SOULEYMANE", "IBRAHIMA SORY", "IBRAHIMA SORRY",
    "IBRAHIMA BARRY", "IBRAHIMA KALIL", "IBRHIM KEDJAN", "IBRAHIME",
    "BOUBACAR", "BOUBACAR SIDDY", "BOUBACAR SADJO", "BOUBACAR2",
    "ABDOUL GADIRY", "ABDOUL KARIME", "FODE MAMOUDOU", "FODE ABDOULAYE",
    "FODE KABA", "FODE MOUSTAPHA", "FODÉ MOHAMED", "FODÉ GASIM",
    "FODÉ OUMAR", "SAA MICHEL", "SAA SEFOU", "SÂA SEFOU", "YAGHOUBA",
    "ALHOUSSENY", "ABDOULAYE SADIO", "ABDOULAYE BILLO", "KABA",
    "TALA OURY", "N'BALYA", "TORAN", "M'BALYA", "MBALLYA", "KEOULEN",
    "GADEL", "NOUMOUN", "WEDRAGO", "SAWA", "PE GBO", "NASSABA",
    "KERIFALA", "DIAKARIA", "MAFATA", "MOUASSA", "MAKOURANI",
    "MAKANBGLE", "GAIYATAI", "GBAMAI", "GONO ACRAN", "JUL", "SIAO",
    "KANIMBA", "BAMBA", "FILFE", "KADIALY", "SADJO", "SORIBA",
    "KOURTIMÉ", "GAMEY", "OYE BALA", "POKPA", "MORIBA OYE",
    "MAMAKÉ", "M'NAMANDJAN", "ODIA KARIFA", "FASOU", "KOI",
    "N'NANDEN MADY", "HAOUSSANE", "MAFRIN", "BOH", "KEROU",
    "SEYDOUBA", "NANKOUMAN", "NASSIRRA", "KALOU", "ISSIAGA",
    "HASSANA", "N'GUASSE", "MAÏSSOU", "VASSIKI", "RISALINE",
    "FANDA", "EZEN", "SALIOU BALLA", "HOUSAY", "DJEBRIL",
    "SAIDOU", "PÔRRE", "ROMAINE", "LAZARD", "MAN", "HBN",
    "TADY", "YT", "III", "O", "A", "M", "K", "VNKX",
]

FEMMES = [
    "SARAN", "BOH SARAN", "AMINATA", "AMINATOU", "AMINATA 2",
    "FATOUMATA", "FATOUMATA BINTA", "FATOUMA", "FATOUMATA DJOULDE",
    "FATOUMATA DIARIOU", "FATOUMATA BHOYE", "FATOUMATA ZACOB",
    "FATOUMATA EVE", "FATOUMATA YARI", "FATOUMATA DIARAYE",
    "FATOUMAT BINTA", "FATOU?ATA BINTA", "FATOUMA BALOU", "FATOUMA BINTA",
    "FATOUMAYA", "FATOU", "FATIM", "FATIME", "FATIMA", "FFATIME",
    "AMA SADIO", "JEYNABE", "AISSATOU", "AISSATOU SADJO",
    "AISSATOU LAMARANA", "AISSATOU LAMARANA BA", "AISSATOU LAMARANA 1",
    "AISSATOU DIOULDE", "AISSATOU KIOUTO", "AISSATOU 2", "AISSATA",
    "AÏSSATOU", "AÏSSATA", "AÏSSATOU LAMARANA", "AÏSSATOU DALANDA",
    "AÏSSATA BAILLO", "AÏSATOU", "AISSA", "AICHA", "AICHA 2", "AÏCHA",
    "AÏSSATA", "NÉNÉ AICHA", "NÉNÉ AÏSSATA 2", "NÈNÈ AÏSSATA",
    "BINTOU", "BINTA", "BINTOU KEITA", "BANASSI", "MAWA", "MAWATA",
    "MAWA KOMARA", "CHITA", "SALEMATOU", "SALIMATOU", "MAIMOUNA",
    "MAÏMOUNA", "KOUMBA", "KOUMBA DIOULDE", "KOUMBA DJOUMA",
    "KOUMBA TÉNIN", "KOUMBA SOYA", "HAWA", "OUMOU HAWA", "OUMOU HAWA 1",
    "OUNMOU HAWA", "ADAMA HAWA", "HAWA GOULI", "HAWA MADY", "HAWA FANTA",
    "MARAIME", "SOUNKARY", "M'MBALLOU", "M'MAH", "MMAWA", "M'MAHAWA",
    "MARIAME", "MARIAMA", "MARIAMA KOLON", "MARIAMA BAÏLO",
    "MARIAMA DJOULDE", "MARIAMA DIOULDE", "MARIAMA NOUMOU",
    "MARIAMA BATOULY", "MARIAMA GANLE", "MARIAMA KINDI", "MARIAMA TELLY",
    "MARIAMA SEYDI", "MARIAMA SADJO", "MARIAMA CIRE", "MARIAMA BENTE",
    "MARIAMABENTHE", "MARIAME AMARA", "MARIAME DALANDA", "MARIAME CIRE",
    "MARIAME DJOUMA", "MARIAME BHOYE", "HADJA MARIAME",
    "HADJA RAMATOULAYE", "HADJA FATOUMATA", "MAMADAMA", "TIGUIDANKE",
    "HABIBATOU", "HABI", "DJENABOU", "DJENEBOU", "DJENEBA", "DJNABOU",
    "DJENE", "DJÉNAB", "DJÉNABOU", "DJENABA OURY", "DJÉNÈ", "DJÈNÈ",
    "OUMOU", "OUMOU LAMARANA", "OUMOU KOULTOUMY", "OUMOU SADJO",
    "OUMOU SALÉ", "MBALLYA", "RAMATA", "RAMATOU", "RAMATOULAYE",
    "N'NAH FANTA", "HOULAYMATOU", "HOUSSAYNATOU", "HOUSSAINATOU",
    "HOUSSAÏNATOU", "ASSIATOU", "ASSETOU", "ASSATA", "FAROUMATA BINTA",
    "NANFADIMA", "N'NAFADIMA", "NEN SIRA", "NENE MARIAMA", "MILKA",
    "GERMAINE", "HARRIETTE", "LEONIE", "MARIE", "CINÈ", "DOURA",
    "GNAMA", "SIA AMY", "SIA", "JEANETTE FATOUMA", "JEANETTE SIA",
    "JEANNETTE SIA", "ANGELINE BINTOU", "GBOKOU ANGELINE", "SADJOUMA",
    "ANSSATA", "SIRA", "SIRA DJOUMA", "TEWA SARAN", "DIARIATOU",
    "DIARIYATOU", "DIARIOU", "KANKOU", "KANKO", "SIA FANTA MALANO",
    "HALIMATOU", "HALUMATOU", "HADIATOU", "ROUGUIATOU", "ROUGUI",
    "ROUGAÏYATOU", "MARLIATOU", "MARIATOU", "DIAMILATOU", "FINDA",
    "NAFINA", "MINATA", "OUMOU LAMARANA", "DJEINABOU", "SAFIATOU",
    "SARATA", "SARANKE", "WATA", "PELA TOUMOUNY", "MAMOUDATOU", "ADJA",
    "MAÏSSOU", "FANDA", "MADIATOU", "BATOUN", "MBALOU", "N'NABINTY",
    "NAGNOUMA", "DJANTOU", "DIADA", "TENIN", "MAMA", "FANTA", "FANTA 2",
    "SONA", "SONAH", "ROSALIE", "FADIMA", "AMINATOU", "HASSANATOU",
    "RABIYATOU", "MABINTY", "MABINTY CHEÏCK", "MABINTOU", "N'MAH",
    "MAKALÉ", "BOUNTOURABY", "BOUNTOU", "KADIATOU", "KADIATOU 2",
    "KADIDIATOU", "KADIA", "MAMATA", "MAMAISSATA", "MAHAWA", "FILLE",
    "YARIE", "MAMOU", "AGNES", "MADO", "BEBE", "CECILE", "THERESE",
    "CHRISTINE", "MMAWA", "BOH FADIMA", "NASSOU", "SIRE", "MAMIE",
    "DELPHINE", "LOUISE", "HELENE", "NEMA", "LEONTINE", "PHILOMENE",
    "THEREZE", "DELPHI'E", "MAMA AISSATA", "AMATOULAYE", "SITAN",
    "DJÂBA", "TAÏBOU", "JOLIE", "NOWAI", "NOWAÏ", "YAMA", "SOUADOU",
    "AISSETOU SARAN", "MAMASATTA", "N'BALOU FATOUMATA 1",
    "N'BALOU FATOUMATA 2", "NANA 1", "NANA 2", "FARAH", "JOSEPHINE",
    "MARIAM", "ISATOU", "KADE", "NANABA", "GNALEN", "SANKOUBA",
    "ALAMACKO", "MAFERING", "DJARAYE", "AHMED ZAROUKA", "MAKHISSA",
    "YARAMON", "GNAKOI", "SENY ESTHER", "ROUGAÏYATOU", "KOU", "ALYA",
    "GNAMALA", "KALIFIYE", "KOUTA", "AYE", "DJESADI", "HAÏBA",
    "NOWAÏ", "SETOU", "SÉTOU", "BATOUN", "PÉ", "MACIRE",
    "TENIN", "SATENIN", "FINA", "BIJOU NAWA", "CLARICE NAWA",
    "ODILON NAWA", "MAKANGBÈ", "MAGANGBÈ", "DANTILY", "SIDAFAN",
    "LANTIRI", "MATENE", "MALON", "KANTI", "DIAMOUNOU", "NACISSE",
    "MASSABORI", "KINDY", "ALIA", "ODIA", "MASSGUE", "N'GOSSE",
    "N'NACIRE", "KADE HOTHIA", "MAIMOUNA", "AISSATOU LAMARANA BA",
]

# Normalisation des marqueurs (numéros, jumeaux, homonymes) à ignorer
SUFFIXES_A_IGNORER = re.compile(r"\s*\d+\s*$")


def normaliser(nom: str) -> str:
    """Majuscules, sans accents, espaces normalisés, sans numéro final."""
    if not isinstance(nom, str):
        return ""
    nom = nom.strip().upper()
    nom = SUFFIXES_A_IGNORER.sub("", nom).strip()
    # supprime les accents pour la comparaison (garde la forme d'origine
    # dans les dictionnaires ci-dessus, mais compare "à plat")
    nom_sans_accent = unicodedata.normalize("NFKD", nom)
    nom_sans_accent = "".join(c for c in nom_sans_accent if not unicodedata.combining(c))
    nom_sans_accent = re.sub(r"\s+", " ", nom_sans_accent).strip()
    return nom_sans_accent


# Dictionnaires normalisés (clé = version sans accent) pour la recherche
def construire_dico(liste):
    return {normaliser(n): n for n in liste}


DICO_HOMMES = construire_dico(HOMMES)
DICO_FEMMES = construire_dico(FEMMES)


def attribuer_sexe(prenom: str):
    """Retourne (code, label) : (1,'Homme') / (2,'Femme') / (None,'') si inconnu."""
    n = normaliser(prenom)
    if n == "":
        return None, ""

    # 1) nom complet
    if n in DICO_HOMMES:
        return 1, "Homme"
    if n in DICO_FEMMES:
        return 2, "Femme"

    # 2) premier mot (le prénom composé garde souvent le genre du 1er mot)
    premier_mot = n.split(" ")[0]
    if premier_mot in DICO_HOMMES:
        return 1, "Homme"
    if premier_mot in DICO_FEMMES:
        return 2, "Femme"

    # 3) non reconnu -> à vérifier manuellement
    return None, ""


def traiter_fichier(chemin_entree: str, chemin_sortie: str,
                     colonne_prenom: str = "P01XA"):
    if chemin_entree.lower().endswith(".csv"):
        df = pd.read_csv(chemin_entree, dtype=str)
    else:
        df = pd.read_excel(chemin_entree, dtype=str)

    if colonne_prenom not in df.columns:
        raise ValueError(
            f"Colonne '{colonne_prenom}' introuvable. "
            f"Colonnes disponibles : {list(df.columns)}"
        )

    resultats = df[colonne_prenom].apply(attribuer_sexe)
    df["P03"] = resultats.apply(lambda t: t[0])
    df["P03_LABEL"] = resultats.apply(lambda t: t[1])
    df["A_VERIFIER"] = df["P03"].isna().map({True: "OUI", False: ""})

    df.to_excel(chemin_sortie, index=False)

    n_total = len(df)
    n_ok = df["P03"].notna().sum()
    n_h = (df["P03"] == 1).sum()
    n_f = (df["P03"] == 2).sum()
    print(f"Total observations       : {n_total}")
    print(f"Sexe attribué automatique: {n_ok} ({n_ok/n_total:.1%})")
    print(f"  dont Hommes            : {n_h}")
    print(f"  dont Femmes            : {n_f}")
    print(f"A verifier manuellement  : {n_total - n_ok}")
    print(f"Fichier ecrit : {chemin_sortie}")


def demo():
    """Exemple avec la liste fournie par l'utilisateur (échantillon)."""
    exemples = [
        "MOUSSA", "AMINATA", "AISSATOU", "MAMADOU", "FATOUMATA", "SEKOU",
        "MARIAMA", "ABDOULAYE", "KADIATOU", "IBRAHIMA", "HAWA", "OUMAR",
        "DJIBRIL", "BINTOU", "ALPHA OUMAR", "THIERNO SADOU", "SIDIBE",
    ]
    df = pd.DataFrame({"P01XA": exemples})
    resultats = df["P01XA"].apply(attribuer_sexe)
    df["P03"] = resultats.apply(lambda t: t[0])
    df["P03_LABEL"] = resultats.apply(lambda t: t[1])
    print(df.to_string(index=False))


if __name__ == "__main__":
    if len(sys.argv) >= 3:
        fichier_entree = sys.argv[1]
        fichier_sortie = sys.argv[2]
        traiter_fichier(fichier_entree, fichier_sortie)
    else:
        print("Usage : python attribuer_sexe_prenoms.py input.xlsx output.xlsx")
        print("Aucun fichier fourni -> exécution d'une démonstration :\n")
        demo()
