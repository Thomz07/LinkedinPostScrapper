# Linkedin scrapper 

Ce script permet de scrapper des personnes sur Linkedin en fonction de leur post dans une entreprise

## Prérequis

- Python 3.10+
- Installer les librairies requises dans l'environnement avec 'pip install -r requirements.txt'
- Bien setup les informations au début du script (identifiants, poste, entreprise, chemin du Excel de sortie)
- Bien être à l'affut si il y a un captcha, il y a 30 secondes pour le faire

Notes : 
Des fois le script se lance trop vite, il y a juste à le relancer
Le script est décrit dans le fichier .py

## Tutoriel
Pour utiliser ce script, il faut d'abord télécharger tous les fichiers de cette repo en cliquant sur :
```
Code -> Download Zip
```
Ensuite ouvrir *cmd* et naviguer jusqu'au répertoir ou le ZIP a été dézippé
```
cd /chemin/vers/mon/dossier
```
Une fois dans le répertoire bien installer les requirements 
```
pip install -r requirements.txt
```
(Si pip ne marche pas essayer 'pip3')

**Bien penser à rentrer les infos au début du fichier python**

**Bien être attentif au potentiel captcha**

Une fois que tout cela est fait éxécuter le fichier Python
```
python Scrap linkedin python.py
```

