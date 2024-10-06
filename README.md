## Relevés Bancaires

Ce petit script en Python permet d'analyser les relevés bancaires reçus au format PDF et de les exporter au format CSV.
Le format Excel est prévu dans le code, non encore terminé.

Il est préférable de créer un environnement Python propre

```
python3 -m venv ./.env
.\.env\Scripts\activate
```

Et ensuite d'importer les requirements

```pip3 install -r .\requirements.txt```


exemple de ligne de commande : 

```./Scanner.py' '--reference-compte' 'LCL' '--scanner' 'LCL' '--output-dir' 'd:/__Logs__/' '--file-pdf' 'c:/Users/xxxxxx/Documents/Banque/Releves/LCL/Releves/305.pdf' '--logs'```

Il est facile de développer son propre module pour ses relevés bancaires en fonction de sa banque. Pour cela on dupliquera le fichier LCL.py exhaustif à renommer par le nom de votre banque par exemple
et le lancer avec votre fichier pdf, un fichier descriptif des pages pdf est crée dans le répertoire déclaré dans --output-dir


Soyez libre de proposer vos propres modules pour vos relevés, je n'ai accès qu'au banques LCL et Boursorama de mon côté.

Ce script permet de façon plus générale (en créant le module ad-hoc) d'extraire n'importe quelle donnée d'un PDF génré par une application.


