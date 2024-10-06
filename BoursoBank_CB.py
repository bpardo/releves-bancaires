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
    "scanner": "BoursoBank_CB",
    "config": {
        "offset_tolerance_ligne": 1,  # Tolérance erreur description ligne
        "detect_header": True,  # détection du header
        "excel_sheet":"Releve-Banque"
    },
    "columns": {
        "date_operation": {
            "flush_previous_line": True,
            "left": 46.2,            
            "post_process":"process_date_operation"
        },

        "libelle_operation": {"left": 131.4, 
                              "post_process":"process_libelle_operation"                             
        },
        
        "date_valeur": {"left": 365.65, "post_process": "process_date_valeur"},
        "debit": {
            "left_min": 500,
            "left_max": 528,
            "currency": True,
            "negative_value": True,
        },
        "credit": {"left_min": 0, "left_max": 0, "currency": True},
        "a_votre_debit":{"left":184.8,"flush_previous_line":True,"post_process":"process_date_debit"},
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
    "ignore_libelle" : []
    
}


# Réservé aux variables dynamiques
dynamic = {}

logger.info(f"Import du module {os.path.splitext(os.path.basename(__file__))[0]}")


def process_date_releve(scanner, text):
    """Extrait la date de départ du relevé ainsi que son numéro"""    
    """ DU JJ.MM.YY AU JJ.MM.YY """
    z = re.findall(r"\b\d+\b", text)

    # Verifications
    if len(z) == 6:
        dynamic["day_report"] = z[0]
        dynamic["month_report"] = z[1]
        dynamic["year_report"] = z[2]
         # chez boursorama pas de numéro de relevé
         # on va donc en créer un fictif année+mois
        dynamic["report_id"] =dynamic["year_report"]+dynamic["month_report"] 

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
            ):
                process_date_releve(scanner, text)
                return True
            
            if "BOUSFRPPXXX" in upper_text:
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
        if left == 502.2 and text == "euros":
            return True


def process_date_operation(scanner, column_item, value) -> None:
    """
    process sur la date operation
    on stocke la date enregistrée par la banque, elle sera surchargée lors de l'évaluation du libellé commencant par "CARTE "
    
    """
    pass

def process_libelle_operation(scanner, column_item, value) -> None:
    # récupère l'année de la date précédement stockée 
    if value.startswith("CARTE "):
        date = value[6:14]     
        day, month, year = date.split('/')
        date = f"{day}/{month}/20{year}"
        scanner.line_export.op_date_operation = date
        scanner.line_export.op_date_valeur = date
        # on supprime "CARTE dd/mm/yy "
        scanner.line_export.op_libelle_operation = value[15:]
        scanner.line_export.op_type_operation = "CB"
            
    

def process_date_debit(scanner, column_item, value) -> None:
    # z = "A VOTRE DEBIT LE "
    # if value.startswith(z):
    #     date = value[len(z):]
    #     # Modifie les dates de valeur avec la date de débit
    pass

def process_flush_operation(scanner, column_item, value):
    scanner.line_export.flush_line()
