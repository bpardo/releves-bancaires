import re
import os
from logger import logger
from ScannerTools import dernier_jour_du_mois


# flush_previous_line : pour signaler la fin de l'opération précédente cela
#                       implique une sauvegarde de la ligne (si elle est complète)
#                       et une remise à zéro des variables de lignes
#
# storage              : nom de la variable pour le stockage de la valeur
#
# left                 : position stricte de la donnée
#
# left_min, left_max   : intervale de position pour la donnée
#
# currency             : formate la valeur en valeur monétaire
# post_process         : nom de la fonction appelée en fin de processus de la donnée


releve = {
    "scanner": "LCL",
    "config": {
        "offset_tolerance_ligne": 1,  # Tolérance erreur description ligne
        "detect_header": True,  # détection du header
        "excel_sheet":"Releve-Banque"
    },
    "columns": {
        "date_operation": {
            "flush_previous_line": True,
            "left": 42.5,
            "post_process": "process_date_operation",
        },
        "libelle_cb": {
            "flush_previous_line": True,
            "storage": "libelle_operation",
            "type_operation": "CB",            
            "left": 50.9,
            "post_process": "process_libelle_cb",
        },
        "detail_cb": {"left": 80.85, "storage": "detail_operation"},
        "date_ancien_solde": {
            "left": 41.9,
            "storage": "date_operation",
            "flush_previous_line": True,
            "post_process": "process_date_operation2",
        },
        "ancien_solde": {
            "left": 268.55,
            "storage": "libelle_operation",
            "type_operation": "#SOLDE_DEPART#",
        },
        "solde_intermediaire": {
            "left": 92.85,
            "flush_previous_line": True,
            "storage": "libelle_operation",
            "type_operation":"#SOLDE_INTERMEDIAIRE#",
            "post_process":"process_date_operation3"
        },
        "totaux": {
            "left": 316.5,            
            "flush_previous_line": True,
            "storage":"libelle_operation",
            "type_operation":"#TOTAUX#",
            "post_process":"process_date_operation3"
        },
        
        "totaux1":{
            "left":319.5,
            "flush_previous_line": True,
            "line_ignore": True           
        },

        "totaux_fin":{
            "left":331.5,
            "flush_previous_line": True,
            "storage":"libelle_operation",
            "type_operation":"#TOTAUX_FIN#",
            "post_process":"process_date_operation3"
        },
        
        "libelle_operation": {"left": 74.85, "list_ignore":"ignore_libelle"},
        "libelle_retrait_dab": {"operation": "DAB", "left": 171.4},
        "detail_operation": {"left": 80.85},
        "date_valeur": {"left": 365.65, "post_process": "process_date_valeur"},
        "debit": {
            "left_min": 380,
            "left_max": 430,
            "currency": True,
            "negative_value": True,
        },
        "credit": {"left_min": 470, "left_max": 500, "currency": True},
        "x_end_page": {
            "left": 519.6,
            "line_ignore": True,
            "flush_previous_line": True,            
        },
        "x_end_document": {
            "left": 35.9,
            "flush_previous_line": True,
            "end_of_document": True            
        },
    },
    "operation_translation": {
        "PRLV": "PRLV",
        "PRELEVEMENT": "PRLV",
        "CHQ.": "CHQ",
        "REM CHQ": "REM CHQ",
        "VIREMENT": "VIR",
        "VIR": "VIR",
        "CB RETRAIT": "CB DAB",
    },
    "ignore_libelle" : ["RELEVE CB AU"]
    
}


# Réservé aux variables dynamiques
dynamic = {}

logger.info(f"Import du module {os.path.splitext(os.path.basename(__file__))[0]}")


def process_date_releve(scanner, text):
    """Extrait la date de départ du relevé ainsi que son numéro"""
    """ AU JJ.MM.YY - N° xxx """
    """ DU JJ.MM.YY AU JJ.MM.YY - N° xxx """
    z = re.findall(r"\b\d+\b", text)

    # Verifications
    if len(z) in [4, 7]:
        dynamic["day_report"] = str(int(z[len(z) - 4]))
        dynamic["month_report"] = str(int(z[len(z) - 3]))
        dynamic["year_report"] = str(int(z[len(z) - 2]))
        dynamic["report_id"] = str(int(z[len(z) - 1]))

        if scanner.page_index == 1:            
            ref = scanner.config.reference_compte
            if not ref is None and ref != "":
                scanner.config.reference_releve_compte = ref + "-" + dynamic["report_id"]
            else:
                scanner.config.reference_releve_compte = dynamic["report_id"]

    else:
        print("<!> Impossible d'extraire la date du relevé")


def detect_header(scanner,page_index):
    """
    Detecte le header de la page pour plus de rapidité
    """
    while True:
        left, top, text = scanner.get_next_line()
        # test si plus de lignes
        if left is None:
            return False

        if page_index==1:
            upper_text = text.upper()
            if (
                ("du".upper() in upper_text)
                & ("au".upper() in text.upper())
                & (" - N°" in text)
            ):
                process_date_releve(scanner, text)
                return True
        else:
            return True
        
        


def detect_first_operation(scanner):
    """
    Cette fonction permet de traiter plus rapidement les opérations
    en détectant l'endroit le plus proche de la première opération

    Pour LCL on détecte cette ligne {'left': 504.35, 'top': 306.837, 'text': 'CREDIT'}
    """
    while True:
        left, top, text = scanner.get_next_line()
        # test si plus de lignes
        if left is None:
            return False

        # Recherche le texte CREDIT en début de page
        if left == 504.35 and text == "CREDIT":
            return True


def process_libelle_cb(scanner, column_item, value):
    """
    Le libellé CB est au format :  TIERS LE DD/MM
    """

    # On cherche le dernier "LE" avant la date
    # pas de split le libéllé du tiers peut contenir "LE"
    try:
        dernier_le = value.rfind("LE")

        scanner.line_export.set_value("libelle_operation", value[:dernier_le].strip())
        scanner.line_export.set_value(
            "type_operation", column_item.get("type_operation", "")
        )

        date_cb = value[dernier_le + 3 :] + "/" + dynamic["year_report"]

        scanner.line_export.set_value("date_operation", date_cb)
        scanner.line_export.set_value("date_valeur", date_cb)
    except:
        scanner.Logger.erreur(
            f"Impossible de parser correctement le libelle CB [{value}]"
        )
        exit(99)


def process_date_operation(scanner, column_item, value) -> None:
    """
    processus de mise au format de l'année
    l'année de l'opération n'est pas disponible sur la colonne
    elle sera rajouté lors du process de date de valeur
    ici on change le séparateur uniquement
    <!> ATTENTION
    <!> vérifier si certaines opération à cheval sur la fin de l'année et la nouvelle posent problème
    """
    z = value.split(".")
    scanner.line_export.op_date_operation = z[0] + "/" + z[1]


def process_date_operation2(scanner, column_item, value) -> None:
    """
    processus de mise au format de la date de l'opération et date valeur pour
    les lignes de totaux
    """
    z = value.replace(".", "/")
    scanner.line_export.op_date_operation = z + "/" + dynamic["year_report"]
    scanner.line_export.op_date_valeur = scanner.line_export.op_date_operation


def process_date_operation3(scanner, column_item, value) -> None:
    """
    processus de mise au format de la date de l'opération et date valeur pour
    les lignes de totaux
    """
    fin_de_mois = dernier_jour_du_mois(f"{dynamic['day_report']}/{dynamic['month_report']}/{dynamic['year_report']}")

    scanner.line_export.op_date_operation = fin_de_mois
    scanner.line_export.op_date_valeur = fin_de_mois



def process_date_valeur(scanner, column_item, value) -> None:
    """
    la date de valeur de l'opération contient l'année
    la date de l'opération non on met donc à jour l'année avec la date de valeur
    """
    value = value.replace(".", "/")
    z = value.split("/")
    # rajoute l'année à la date d'opération
    scanner.line_export.op_date_operation = (
        scanner.line_export.op_date_operation + "/20" + z[2]
    )
    scanner.line_export.op_date_valeur = z[0] + "/" + z[1] + "/20" + z[2]


def process_flush_operation(scanner, column_item, value):
    scanner.line_export.flush_line()
