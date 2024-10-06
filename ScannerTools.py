import os
from datetime import datetime
from calendar import monthrange
import decimal

def create_output_structure(output_dir):
    """Crée un répertoire et ses sous-répertoires si nécessaire.

    Args:
      output_dir: Le chemin du répertoire principal à créer.
    """

    # Vérifier si le répertoire principal existe déjà
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Créer les sous-répertoires
    subdirectories = ["traites", "rejets", "_tmp","_logs"]
    for subdir in subdirectories:
        subdir_path = os.path.join(output_dir, subdir)
        if not os.path.exists(subdir_path):
            os.makedirs(subdir_path)



def str_to_decimal(value):
    # Convertir en Decimal directement
    try:
        # Remplacer les virgules par des points, si nécessaire
        value = value.replace(',', '.').replace(" ","")
        # Convertir en Decimal
        value = decimal.Decimal(value)
        # Arrondir à deux chiffres après la virgule
        return value.quantize(decimal.Decimal('0.00'), rounding=decimal.ROUND_HALF_UP)        
    except:
        return decimal.Decimal("0.00")                


def strToFloat(value, default_value=0.0):
    """
    Convertit une chaîne en flottant.

    Args:
      string: La chaîne à convertir.
      default_value: La valeur à retourner si la conversion échoue.

    Returns:
      Le flottant correspondant à la chaîne, ou la valeur par défaut.
    """

    value ="" if value is None else value

    # Remplacer toutes les virgules par des points
    value = value.replace(',', '.')
    # Supprimer tous les espaces
    value = value.replace(' ', '')

    try:
        # Convertir la chaîne nettoyée en Decimal
        decimal_value = Decimal(value)
        # Arrondir à deux chiffres après la virgule
        decimal_value = decimal_value.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)
        return decimal_value
    except (ValueError, InvalidOperation):
        # Gérer le cas où la conversion en Decimal échoue
        decimal_value = Decimal(value)
        # Arrondir à deux chiffres après la virgule
        decimal_value = decimal_value.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

    return decimal_value





def strToFloatStr(value, default_value=0.0):
    """
    convertie une value en value représentant un float
    """
    if not value:
        return "0.00"
    else:
        return str(value).replace(",", ".").replace(" ", "")


def strFloatToExport(value):
  """
    convertie une valeur string représentant un float vers une valeur exportable 
  """
  if not value:
    return ""
  else:
    try:
        return float(str(value).replace(",", ".").replace(" ", ""))
    except:        
        return ""
    




def is_prefixe(ignore_list, valeur):
  """Vérifie si une chaîne de la liste ignore_list est le début de la chaîne valeur.

  Args:
    ignore_list: Une liste de chaînes à vérifier.
    valeur: La chaîne à comparer.

  Returns:
    True si l'une des chaînes de ignore_list est un préfixe de valeur, False sinon.
  """

  for prefix in ignore_list:
    if valeur.startswith(prefix):
      return True
  return False


def dernier_jour_du_mois(date_str):
  # Convertir la chaîne de caractères en objet datetime
  date_obj = datetime.strptime(date_str, "%d/%m/%Y")

  # Obtenir le dernier jour du mois
  dernier_jour = monthrange(date_obj.year, date_obj.month)[1]

  # Construire la date du dernier jour du mois
  derniere_date = datetime(date_obj.year, date_obj.month, dernier_jour)

  # Formater la date au format dd/mm/yyyy
  return derniere_date.strftime("%d/%m/%Y")