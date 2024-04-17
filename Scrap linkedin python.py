from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from time import sleep
import pandas as pd

User = ""
Password = ""

ListePoste = ["RH", "DRH"] 
Entreprise = "Orange"

ExcelSortie = "C:\\Users\\Ohlone\\Desktop\\Entreprises.xlsx" # bien mettre des double antislash

df = pd.DataFrame(columns=['Poste', 'Nom', 'Prénom', 'Entreprise']) # Dataframe pour le Excel final

# Initialisation du navigateur
firefox_options = Options()
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=firefox_options)
driver.get("https://linkedin.com")
driver.maximize_window()
wait = WebDriverWait(driver, 10) 
actions = ActionChains(driver)

# Accepter les cookies
xpathCookies = '//*[@action-type="ACCEPT"]'
wait.until(EC.presence_of_element_located((By.XPATH, xpathCookies))).click() 

# Connexion à linkedin
champUserName = wait.until(EC.presence_of_element_located((By.ID, "session_key")))
champPassword = wait.until(EC.presence_of_element_located((By.ID, "session_password")))
boutonOK = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@data-id="sign-in-form__submit-btn"]')))
champUserName.send_keys(User)
champPassword.send_keys(Password)
boutonOK.click() 

# Check du captcha - 30 secondes pour le faire 
try:
    driver.find_element(By.ID, "captcha-internal")
    print("Il y a un captcha, veuillez le résoudre")
    WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "search-global-typeahead__input")))
except Exception:
    print("Pas de captcha")

# Recherche de l'entreprise
barreRecherche = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "search-global-typeahead__input")))
barreRecherche.send_keys(Entreprise+Keys.ENTER) 

# Loop dans la liste de posts
for postActuel in ListePoste:

    # Check de la présence du boutons 'Tous les filtres' car pour certaines entreprises il faut faire une manip un peu tricky pour qu'il apparaisse
    try:
        wait.until(EC.presence_of_element_located((By.XPATH, '//*[@aria-label="Afficher tous les filtres. En cliquant sur ce bouton, toutes les options de filtres disponibles apparaîtront."]'))).click()
        print("Bouton 'Tous les filtres' présent")
    except TimeoutException:
        print("Bouton 'Tous les filtres' pas présent")
        compteur = 0
        for filter in wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "search-reusables__primary-filter"))):
            compteur = compteur + 1
            if compteur == 3: # Manière très barbare pour cliquer sur 'Personnes' - peut être revoir la méthode
                filter.click()
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@aria-label="Afficher tous les filtres. En cliquant sur ce bouton, toutes les options de filtres disponibles apparaîtront."]'))).click()

    compteur = 0
    motsclésliste = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "mt1"))) # Pareil manière trés barbare de loop dans les 6 champs de mots clés car ceux ci n'ont pas d'identifiants distincts
    for motsclé in motsclésliste:
        compteur = compteur + 1
        if compteur == 1:
            motsclé.click()
            actions.send_keys(Keys.TAB).perform()
            actions.send_keys(Keys.TAB).perform()
            actions.send_keys(Keys.TAB).perform()
            actions.send_keys(Keys.TAB).perform()
            actions.send_keys(Keys.TAB).perform()
            actions.send_keys(Keys.ENTER).perform() # C'est barbare mais ça permet de réinitialiser les filtres
            sleep(2)
        if compteur == 3: # Le champ Poste est le 3ème
            motsclé.send_keys(postActuel)
        if compteur == 4: # Le champ Entreprise est le 3ème
            motsclé.send_keys(Entreprise)

    # On applique les filtres
    filtres = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@aria-label="Appliquer les filtres actuels pour afficher les résultats"]')))
    filtres.click()

    # Récupération du nombre total de résultats de la recherche
    nombreResultats = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "pb2"))).text
    nombreResultats = int(nombreResultats[:3])  # Ajuster ici si le format du texte est différent
    print(" ")
    print("Recherche pour l'entreprise", Entreprise, "concernant le post :", postActuel)
    print(nombreResultats)

    compteurTotal = 0
    compteurNombrePersonnes = 0
    continuer = True
    while continuer:
        # Récupération des groupes de personnes après chaque changement de page pour éviter StaleElementReference
        groupes_personnes = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ph0")))
        for groupe in groupes_personnes:
            # Réinitialisation de la recherche des éléments 'li' à chaque tour de boucle
            personnes = groupe.find_elements(By.TAG_NAME, "li")
            for personne in personnes:
                lignes = personne.text.split('\n')
                nom_prenom = lignes[0] if len(lignes) > 0 else None
                poste = lignes[4] if len(lignes) > 4 else None

                if "Filtrez" in nom_prenom:
                    print("Case sales navigator")
                else:
                    compteurNombrePersonnes += 1
                    compteurTotal += 1
                    if compteurTotal >= nombreResultats:
                        print("Nombre de personnes recherché atteint ou dépassé.")
                        continuer = False
                        break

                    if nom_prenom:
                        nom, prenom = nom_prenom.split(' ')[0], ' '.join(nom_prenom.split(' ')[1:])
                    else:
                        nom, prenom = None, None

                    # Ajout des infos dans le Dataframe
                    df = df._append({'Poste': poste, 'Nom': nom, 'Prénom': prenom, 'Entreprise': Entreprise,'Poste recherché': postActuel}, ignore_index=True)
                    print(compteurTotal)

        if not continuer:
            break

        # Changement de page s'il reste encore des résultats à parcourir
        if compteurNombrePersonnes >= 11:
            try:
                actions = webdriver.ActionChains(driver)
                actions.send_keys(Keys.END).perform()  # Assurer que le bouton suivant est visible
                next_button = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.artdeco-pagination__button--next[aria-label='Suivant']")))
                next_button.click()
                compteurNombrePersonnes = 0  # Réinitialiser le compteur pour la nouvelle page
            except Exception as e:
                print("Erreur lors du changement de page ou dernière page atteinte.", e)
                continuer = False

# On écrit le Dataframe dans le Excel
df.to_excel(ExcelSortie, index=False)