
import csv
import datetime
import os
import time

import numpy
from selenium.common.exceptions import NoSuchElementException, NoSuchWindowException, StaleElementReferenceException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def current_milli_time():
    return round(time.time() * 1000)

def uscita():
    print("Hai chiuso la finestra quindi esco")
    exit()


# PARAMETRI
#LINK = "https://sitemanager.ability.abb"
LINK = "https://stage.new.sitemanager.ability.abb/#/"
mailabb = "marco.scorta@it.abb.com"
passwordabb = "robimar65@@"

chrome_driver = ChromeDriverManager().install()
chrome_options = Options()
driver = Chrome(service=Service(chrome_driver), options=chrome_options)
i = 0


def verificaNumero(domanda):
    while True:
        continua = input(domanda)
        if continua.isnumeric():
            return int(continua)
        else:
            print("Risposta non valida!")

def creacartella(nome):
    try:
        if not os.path.exists(nome):
            os.makedirs(nome)
    except:
        return 0
    return 1

def creaCsvIntermedio(dati,base):
    if not os.path.exists(base+"/dataset.csv"):
        with open(base + "/dataset.csv", 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Pagina","DT", "TC", "Timeouts"])
            writer.writerow(dati)
    else:
        with open(base + "/dataset.csv", 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(dati)

def creacsv(a,base,inizio):
    newbase = base + "/CSV"
    creacartella(newbase)
    with open(newbase + "/dataset.csv", 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["DT","TC","Timeouts"])
        numpy.savetxt(file, tot, delimiter=",", fmt='%1.0f')

def login(conferma):
    driver.implicitly_wait(20)
    driver.get(LINK)  # Apre il link

    if conferma != "M":
        while True:
            try:
                driver.find_element(By.CLASS_NAME, 'signin').find_element(By.CLASS_NAME, 'button').click()

                driver.find_element(By.ID, 'i0116').send_keys(mailabb)

                driver.find_element(By.ID, 'idSIButton9').click()

                driver.find_element(By.ID, 'txtUsername').send_keys(mailabb)
                driver.find_element(By.ID, 'txtPassword').send_keys(passwordabb)

                driver.find_element(By.ID, 'btnSubmit').click()
                break
            except NoSuchWindowException:
                print("Hai chiuso la finestra quindi esco")
                exit()
            except:
                print ("Si è verificato un errore. Rifaccio il login")

    while True:
        continua = input(
            "Sto caricando la pagina. Inserisci i tuoi dati e quando sei nella DASHBOARD premi C per continuare: ")
        if continua == 'C':
            print("Adesso inizio il test: non toccare il browser.")
            return 1
        else:
            print("Risposta non valida")

# -----------------------------------------------------------------------------
# FUNZIONI RIGUARDANTI I TEST

def presenzaElemento(elemento): #Controlla se un elemento è presente oppure no
    element_visible = False
    try:
        driver.implicitly_wait(0)
        element_visible = driver.find_element(By.CLASS_NAME, elemento).is_displayed() #Controlla se elemento visibile nel dom
    # Se non c'è torna 0
    except NoSuchElementException:
        return 0
    except StaleElementReferenceException:
        print("...")
    except:
        return 0
    if element_visible == False:
        return 0
    # Altrimenti torna 1
    return 1

def loadTime(link, timemax):
    # Mentre presenzaElemento si occupa semplicemente di dire se un elemento esiste oppure no
    # qui si calcola il tempo in cui l'elemento resta visibile.
    # Se l'elemento cercato è un loader di caricamento, il tempo da quando viene aperta la pagina
    # a quando sparisce il loader è quello ricercato

    if "https://" in link: #Se è un vero link (http://)
        while True:
            try:
                driver.get(link)  # Apre il link
            except:
                print("Si è verificato un timeout... aspetto un po' e riprovo")
                time.sleep(10)
            break
    else: # Se non è un vero link, è un percorso con css
        time.sleep(3)
        try:
            driver.implicitly_wait(10)
            driver.find_element(By.XPATH, '//*[text()="'+link+'"]').click()
        except:
            print("Elemento non trovato!")
            return -1
    inizio = current_milli_time()
    flag = 0
    counter = 0
    mat = []
    while True:
        rect = presenzaElemento("rect1")
        spinner = presenzaElemento("spinner-icon-dot")
        current = current_milli_time() - inizio
        mat.append([rect, spinner, current])
        print("Rect:" + str(rect) + " - " + "Spinner: " + str(spinner) + " " + str(current))

        # Nel nostro caso i loader possono essere 2 ed inoltre ci può essere qualche millisecondo di attesa fra
        # l'istante in cui sparisce il primo loader e l'istante in cui compare il secondo.
        # Per questo motivo bisogna calcolare il tempo del primo loader, continuare a monitorare per un tot.
        # _ se non compaiono altri loader, il tempo del primo loader è il tempo di caricamento
        # _ altrimenti si aspetta fino a quando sparisce il secondo loader

        if (current > timemax) and flag == 0:
            return current

        if rect == 0 and spinner == 0:
            flag = 1

        # Questa variabile flag va a 1 nel momento in cui entrambi i loader sono a 0.
        # Ipotizziamo che il primo loader abbia finito e il secondo non si sia ancora caricato

        if flag == 1:
            if rect == 0 and spinner == 0:
                counter = counter + 1
            else:
                counter = 0
                flag = 0
        if counter == 100:
            break
    print("Finito")

    # Per 100 volte continuo a controllare. Se non compare altro, restituirò l'ultimo valore utile
    # Ovvero l'ultimo valore di tempo calcolato prima dei 100 ulteriori controlli.
    # Se invece compare l'altro loader, questo flag va a 0 ed il tempo continua a incrementare fino
    # a quando non spariscono nuovamente entrambi e si ritorna nel flag.

    print(mat[len(mat) - 100][2])
    return(mat[len(mat) - 100][2]) #Alla fine ritorno il tempo calcolato

def lastLoadTime(link, ricalcolo, timemax):
    # La funzione loadTime si occupa di restituire il tempo calcolato ignorando il fatto che questo rispetti o meno
    # il timeout.
    # Quando il programma viene eseguito l'utente inserisce MILLISECONDI DI TIMEOUT, NUMERO DI TENTATIVI PER PAGINA
    # L'idea è che una pagina possa crashare. Se una pagina crasha superando il tempo di timeout impostato dall'utente
    # si riprova dicendo, per esempio, che c'è stato un timeout, ma al secondo tentativo la pagina ha rispettato il
    # tempo di caricamento.

    contatimeout = 0
    datornare = []
    for c in range(int(ricalcolo)):  # per un max di tot volte
        tempo = loadTime(link, timemax)  # calcola il tempo
        i = datetime.datetime.now()
        dt = "%s-%s-%s - %s:%s:%s" % (i.year, i.month, i.day, i.hour, i.minute, i.second)

        if tempo > timemax:  # se il tempo calcolato è maggiore del timeout
            print("Timeout")
            contatimeout = contatimeout + 1  # aggiunge 1 al contatore timeout e ripete il test
        elif tempo < 0:  # se il tempo calcolato è < 0
            tempo = 0  # lo porta a 0 e ripete il test
        else:  # altrimenti
            print("Non ricalcolo! ultimo tempo calcolato:" + str(tempo) + ", timeout precedenti: " + str(contatimeout))
            return [dt, tempo, contatimeout]  # Ritorno il datetime, il tempo di caricamento della pag e il numero di timeout

        if c == (ricalcolo-1):
            print("E' andato per " + str(ricalcolo) +" volte in timeout ma devo ritornare:")
            return [dt, tempo, contatimeout]

    return datornare

def testPagina(pagina, link, ricalcolo, timemax, base):
    vettore = [pagina] + lastLoadTime(link, ricalcolo, timemax)
    creaCsvIntermedio(vettore,base)
    return (vettore)

def testLista(lista, ricalcolo, timemax, base):
    i = 0
    provelista = []
    for i in range(len(lista)): # Per ogni elemento della lista
        print("Sto testando: " + str(lista[i][0]))
        provelista.append(testPagina(lista[i][0], lista[i][1], ricalcolo, timemax, base))
    return provelista


def test(lista, timemax, giri, ricalcolo,aspetta,base):
    vettoregiri = []
    for j in range(int(giri)):
        print("Giro " + str(j + 1))
        vettoregiri.append(testLista(lista,ricalcolo, timemax, base))
        # Serve per aspettare tot secondi fra un giro e l'altro
        aspettatime = current_milli_time()
        if j != (giri-1): #Se non è l'ultimo giro fai aspettare altrimenti finisci
            while (current_milli_time() - aspettatime) < aspetta:
                print("Mancano " + str(round((aspetta - (current_milli_time() - aspettatime)) / 1000)) + " secondi")
                time.sleep(1)
    print (vettoregiri)





def inizia():
    giri = verificaNumero("Quanti giri vuoi fare? ")
    ricalcolo = verificaNumero("In caso di timeout, quante volte vuoi ricontrollare quella pagina? (consigliato 2): ")
    timemax = verificaNumero("Inserire il tempo in ms come timeout (consigliato 10000): ")
    aspetta = verificaNumero("Quanto vuoi aspettare fra un giro e l'altro? ")
    i = datetime.datetime.now()
    dt = "%s-%s-%s - %s.%s.%s" % (i.year, i.month, i.day, i.hour, i.minute, i.second)
    base = "TEST/"+dt

    lista = [
        ["Gerarchica","https://sitemanager.ability.abb/#/assetpage/view2d3d"]
    ]

    if creacartella(base+"/CSV"): #Creo la cartella timestamp contenente CSV
        test(lista, timemax, giri, ricalcolo, aspetta, base)

if login("M") == 1:
    inizia()



