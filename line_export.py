from logger import logger
from ScannerTools import *
import re


class Line_Export:

    def __init__(self, config, params):
        self.config = config
        self.params = params
        self.clear_line()
        self.module_scanner = params.releve["scanner"]        
        self.index_line = 0
        self.op_index_line=0

    def __str__(self):
        credit = "" if self.op_credit == None else str(self.op_credit)
        debit = "" if self.op_debit == None else str(self.op_debit)
        type_operation = (
            "" if self.op_type_operation == None else str(self.op_type_operation)
        )
        detail_operation = (
            "" if len(self.op_detail_operation) == 0 else self.op_detail_operation
        )

        return f"{self.module_scanner};{self.config.reference_releve_compte};{self.op_index_line};{self.op_date_operation};{self.op_libelle_operation};{type_operation};{self.op_date_valeur};{debit.replace('.',',')};{credit.replace('.',',')};;;;{'|'.join(detail_operation)}"

    def get_header(self):
        return "Scanner_Module;Reference_compte;N° ligne;Date_operation;Libelle_operation;Type_operation;Date_valeur;Debit;Credit;Poste principal;Poste secondaire;Notes;Detail_operation"

    def clear_line(self):
        self.line_ignore = False

        # proriétés exportables du relevé
        self.module_scanner = self.params.releve["scanner"]

        self.op_date_valeur = ""
        self.op_libelle_operation = ""
        self.op_type_operation = ""
        self.op_date_operation = ""
        self.op_credit = ""
        self.op_debit = ""
        self.op_detail_operation = []
        self.op_index_line=""

    def set_value(self, colonne, valeur):
        """
        Stocke la valeur dans la bonne variable
        """
        attribut = f"op_{colonne}"
        if hasattr(self, attribut):
            if type(getattr(self, attribut)) == list:
                # variables de type tableau
                getattr(self, attribut).append(valeur)
            else:
                # autres variables
                setattr(self, attribut, valeur)
        else:
            error_message = f"line_export.py:set_value - L'attribut op_{colonne} n'exite pas dans la classe Line_Export."
            logger.error(error_message)

    def get_value(self, colonne, valeur_defaut):
        """
        Récuère la valeur d'une variable
        """
        attribut = f"op_{colonne}"
        if hasattr(self, attribut):
            if type(getattr(self, attribut)) == list:
                # variables de type tableau
                return getattr(self, attribut)
            else:
                # autres variables
                return getattr(self, attribut)
        else:
            error_message = f"line_export.py:get_value - L'attribut op_{colonne} n'exite pas dans la classe Line_Export."
            logger.error(error_message)


    def is_ok_to_flush(self):
        try:
            return self.op_date_operation != "" and self.op_libelle_operation != "" and (self.op_credit != "" or self.op_debit != "")        
        except:
            return False

    def flush_line(self):
        """
        Retourne une ligne complete
        si les conditions sont réunies
        à savoir : la ligne n'est pas marquée comme ignorée
        les informations minimales sont présentes
        """
        if self.line_ignore:
            logger.debug(f"Ligne ignorée pour l'export")
            self.clear_line()
            return None

        special_line = self.op_type_operation.startswith("#") and self.op_type_operation.endswith("#") and  len(self.op_type_operation) > 2
            
        if self.is_ok_to_flush():
            if special_line:
                # forme un nom de variable
                var_name = re.findall(r"#(.*?)#", self.op_type_operation)[0].replace(" ", "_")
                logger.info(f"  Détection sous total : {var_name}")
                credit_value = str_to_decimal(self.op_credit)
                debit_value = str_to_decimal(self.op_debit)

                var_value = self.params.dynamic.get(var_name, decimal.Decimal("0.00"))
                
                logger.info (f"    Calcul : {var_value} + {credit_value} - {debit_value}")

                var_value = var_value + credit_value - debit_value
                logger.info(f"      Valeur affectée {var_value}")

                self.params.dynamic[var_name] = var_value
                self.clear_line()

                # c'est une ligne de totaux on ne l'exportera pas dans la liste 
                return None
            else:
                # ce n'est pas une ligne spéciale on va sommer les crédits et débits
                credit_value = str_to_decimal(self.op_credit)
                debit_value = str_to_decimal(self.op_debit)

                total_credit = self.params.dynamic.get("TOTAL_CREDIT", decimal.Decimal("0.00"))+credit_value
                total_debit = self.params.dynamic.get("TOTAL_DEBIT", decimal.Decimal("0.00"))+debit_value

                logger.info(f"  credit {credit_value}, débit {debit_value}")
                self.index_line+=1
                self.op_index_line = self.index_line

            out_str = str(self)
            logger.debug(f"export ligne {out_str}")
            self.clear_line()
            return out_str
        else:
            logger.warn(f"La ligne {str(self)} n'est pas exportable, elle contient des variables non valorisées")                        
            self.clear_line()
            return None

