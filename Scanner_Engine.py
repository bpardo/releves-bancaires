from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Tuple
import re
from ScannerTools import * # trToFloat, strToFloatStr, is_prefixe, dernier_jour_du_mois
from line_export import Line_Export
from math import isclose
from decimal import Decimal

from logger import logger


class Scanner:
    def __init__(self, config, params, filename):

        self.lines = []
        self.config = config
        self.params = params
        self.filename = filename
        self.page_index = 0
        # stocker la ligne courante en cours d'extraction pour le parsing
        self.parser_line = 0
        self.output_lines = []
        # ligne en cours d'évaluation
        self.line_export = Line_Export(config, params)

    def load_lines(self, lines):
        self.lines = lines
        # réinitialise l'index du parseur de ligne
        self.parser_line = 0

    def get_next_line(self):
        """
        Retourne la prochaine ligne et incrémente l'index de scan
        """
        if self.parser_line >= len(self.lines):
            left = None
            top = None
            text = None
        else:
            left = self.lines[self.parser_line]["left"]
            top = self.lines[self.parser_line]["top"]
            text = self.lines[self.parser_line]["text"]
            self.parser_line += 1
        return (left, top, text)

    def is_column(self, code_column, left) -> bool:
        """
            Determine si les coordonnées correspondent
            à l'emplacement de la colonne code_column
        """
        col = self.params.releve["columns"][code_column]
        if "left_min" in col and "left_max" in col:
            return left >= col["left_min"] and left <= col["left_max"]
        elif "left" in col:
            return isclose(left, col["left"])
        # else:
        #     logger.error(f"La définition de la colonne [{code_column}] n'est pas conforme dans le module ")

    def detect_data(self, left, top, text):
        """
            Detecte le type de donnée
            en parcourant toutes les colonnes définies dans le paramétrage du module scanner utilisé
        """
        cols = self.params.releve["columns"]

        for key in cols.keys():
            if self.is_column(key, left):
                logger.debug(f"Analyse : Left:{left}, Top:{top}, [{text}] => {key}")
                return key

        # donnée non non répertoriée on passe
        logger.debug(f"Analyse : Left:{left}, Top:{top}, [{text}] => None")
        return None

    def get_current_line(self):
        """
            Retourne la valeur de la dernière valeur lue
            prend la valeur de la ligne précédente car la lecture par
            get_next_line a fait avancé le curseur de ligne
        """
        if self.parser_line >= len(self.lines):
            left = None
            top = None
            text = None
        else:
            left = self.lines[self.parser_line - 1]["left"]
            top = self.lines[self.parser_line - 1]["top"]
            text = self.lines[self.parser_line - 1]["text"]
        return left, top, text

    def process_page(self, page_index, lines) -> bool:
        """
            Process d'une page du PDF
        """
        self.page_index = page_index
        self.load_lines(lines)

        # Détection du header ?
        if self.params.releve["config"]["detect_header"]:
            if not self.params.detect_header(self,page_index):
                logger.error(f"Impossible de trouver le header sur la page {page_index}")                
                return True

        # Recherche le début des opérations
        if not self.params.detect_first_operation(self):
            print(f"<!> Impossible de détecter le début des opérations sur la page {page_index}")
            return True

        # process des opérations
        left, top, text = self.get_next_line()

        # Pour chaque élément du PDF
        while not left is None:
            
            # détection de la donnée
            # on vérifie quell est le type de donnée
            column_name = self.detect_data(left, top, text)
            if column_name is None:
                # donnée non connue on passe à la suivante
                left, top, text = self.get_next_line()
                continue

            # Un type de colonne a été détecté
            logger.debug(f"{column_name.ljust(15)} : {text}")

            # Accès rapide à la description de la donnée de la colonne
            column_item = self.params.releve["columns"][column_name]
            
            # Est-ce une nouvelle opération ?
            # ou une rupture de bloc de donnée
            if column_item.get("flush_previous_line", None):
                # on exporte la ligne d'opération précédente
                _txt = self.line_export.flush_line()
                if not _txt is None:                    
                    self.output_lines.append(_txt)                    

            ### TRAITEMENT DE LA NOUVELLE LIGNE ###

            if column_item.get("end_of_document", False):
                # Marqueur de fin de document on stoppe tout
                break

            # doit on ignorer l'information en fonction du texte
            iList = column_item.get("list_ignore",None)
            if iList:
                # vérifie si la liste est définie
                if self.params.releve[iList]:
                    if is_prefixe(self.params.releve[iList],text):                    
                        self.line_export.line_ignore=True                        

            # Ligne ignorée pour l'export
            if column_item.get("line_ignore", False):
                self.line_export.line_ignore = True

           
            # Ignore_value
            if not column_item.get("ignore_value", False):
                # Valeur non ignorée on la traite                                
                column_storage = column_item.get("storage", column_name)
                # on vérifie où on doit stocker la valeur                
                self.line_export.set_value(column_storage, text)                   
                # type d'operation
                type_operation = column_item.get("type_operation",None)
                if not type_operation is None:
                    self.line_export.set_value("type_operation", type_operation)
                    if type_operation.startswith('#') and type_operation.endswith('#') and len(type_operation) > 2:
                        # variable spéciale
                        pass
                    
               
            # Post process sur la colonne
            post_process = column_item.get("post_process", None)
            if not post_process is None:
                # vérifie que la fonction est disponible dans le scanner
                if not hasattr(self.params, post_process):
                    error_messsage = f"La fonction {post_process} n'est pas implémentée dans le module {self.params.releve['scanner']}"
                    logger.error(error_messsage)
                    exit(99)
                else:
                    # execute la fonction définie le dictionnaire
                    getattr(self.params, post_process)(self, column_item, text)

            # ligne suivante
            left, top, text = self.get_next_line()

        # Plus de données on flush
        _txt = self.line_export.flush_line()
        if not _txt is None:
            self.output_lines.append(_txt)            
        return True
