import multiprocessing
from datetime import date
import pandas as pd
from openpyxl import load_workbook

def my_function(model, size, return_dict):
    from bs4 import BeautifulSoup
    from selenium import webdriver  # selenium is a bit slower than bs
    import time

    try:
        driver = webdriver.Chrome(r'C:\chromedriver.exe')
        url = 'https://stockx.com/{}'                       #molt bona solució a com ficar el argument model dintre de la url sense '' del string!!!
        url = url.format(model)

        driver.get(url)
        # time.sleep(0.1)        #not needed since counter starts when web is fully loaded
        #Per a cada botó, busco un propietat característica per la que caracteritzar-lo (o un del seuse fills almenys) per poder accedir a ell)
        driver.find_element_by_xpath("//button[@aria-label='Close']").click()       #Trec el pop up del mig de la pàgina
        #time.sleep(0.4)
        #driver.find_element_by_xpath('// *[ @ id = "root"] / div[2] / div[2] / button').click()
        driver.find_elements_by_xpath('//button[contains(text(), "Okay")]')[0].click()                 #Trec allò de baix la pàgina, sols hi ha un element amb Okay, fico [0] perquè me trona una llista de un element
        time.sleep(6)
        driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/span/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div/div/button').click()  # la id del button va canviant, llavors no puc per xpath---->fico fullxpath     (comú per a tots els models!)
        # driver.find_element_by_xpath('/html/body/div[1]/div[1]/div[2]/div[2]/span/div[2]/div[1]/div[1]/div[1]/div[2]/div[1]/div/div/div/div/div/div[2]/ul/li[5]').click()      #xpath de la talla que jo tinga//això s' haurà de canviar!
        # driver.find_elements_by_xpath("//div[contains(., 'us 7')]").click()                                #ni de broma això és on he de clicar, això és el text que vull identificar!
        # driver.find_elements_by_xpath('//div[contains(.,"us 7")]//parent::div//parent::div').click()        #això es tirar un div cap enrere, encara necessito tirar un nivell mes cap a enrere
        ruta = '//div[contains(.,"us {}")]/ancestor::li'
        rutareal = ruta.format(size)
        #time.sleep(2)
        element = 0
        lio = driver.find_elements_by_xpath(rutareal)

        if (size>9.5):
            #elem = driver.find_elements_by_class_name('select-options')[1]      #resulta ser el segon element el que busco, ho he comparat amb find per xpath
            #box = elem.find_element_by_xpath('..')                              #tiro un nivell cap a enrere, són el mateix, comprovat igual
            #o faig scroll a una o a l' altra
            #no necessito allò que he de fer scroll, solament fins a on! un poc xanxullo perquè faré scroll a tot i després corregiré
            rutafinal = ruta.format(14)                                             #element prou abaix com per aque al buscar-lo tire prou cap a baix
            boxsizefinal = driver.find_elements_by_xpath(rutafinal)[1]
            driver.execute_script("arguments[0].scrollIntoView();", boxsizefinal)           #fa scroll a tota la pàgina, però també dintre d' on jo vull!
            #time.sleep(0.1)

            namemodel = driver.find_elements_by_class_name('name')[0]
            driver.execute_script("arguments[0].scrollIntoView();", namemodel)           #fa scroll cap a dalt fins al títol per tenir-ho tot en ordre, però el inner-menu scrollejat!

            while element <= (len(driver.find_elements_by_xpath(rutareal))):
                try:
                    lio[element].click()
                    break
                except:
                    pass
                element = element + 1

            driver.find_elements_by_xpath(rutareal)[0]      #Un poc cutre, pero gets the job done.
            #Provoco un error si la size no està al registre fent-li accedir

            #if condition():
                #break

            time.sleep(5)  # m' espero per a que pugi llegir correctament la pàgina carregada
            res = driver.execute_script('return document.documentElement.innerHTML')  # page source after loaging fully
            driver.quit()  # close window



        else:
            #driver.find_elements_by_xpath(rutareal)[0].click()  # acabo de demostrar que el element és el mateix, lo unic que ara no el puc clicar!!! ara se suposa que això és una llista!! de fet, és el segon element de la llista perque he mirat com coincidia el elemnet number de la variable!

            while element <= (len(driver.find_elements_by_xpath(rutareal))):
                try:
                    lio[element].click()
                    break
                except:
                    pass
                element=element+1

            # ara ja estic on vull, extrec el codi html carregat a tope
            time.sleep(5)       #m' espero per a que pugi llegir correctament la pàgina carregada
            res = driver.execute_script('return document.documentElement.innerHTML')  # page source after loaging fully
            driver.quit()  # close window

        soup = BeautifulSoup(res, 'html.parser')  # something was going wrong with lmxl, i swap to html.parser
        # '//*[@id="latest-sales-table"]/tbody/tr[1]/td[2]'

        table = soup.find('table', {'class': 'latest-sales table table-striped table-condensed'})  # crec que el findall es irrellevant, sol hi ha una taula com esta / també hagués pogut fer el soup.table
        # aquesta linia es per veure com va el codi

        #try:
        table_rows = table.find_all('tr')
        prices = []
        for tr in table_rows:
            td = tr.find_all('td')
            if len(td) > 0:  # me fumo los headings
                 row = [i.text for i in td]
                 # print(row)
                 prices.append(row[1])

        prices = ' '.join(prices).replace('€', '').split()  # trec el € de tots els elements

        total = 0

        newprices = []                  #per poder operar si els preus són gran i venen donats per ,s
        for element in range(0, len(prices)):
            newprices.append(prices[element].replace(",", ""))

        for element in range(0, len(newprices)):
            total = total + int(newprices[element])
        aver = total / len(newprices)
        maxpr = max(newprices)

        if (int(maxpr) - int(aver)) < 0.35 * int(aver):  # Percentatge arbitrari, es per a que les dades siguin fiables
            #print(str(aver), '€', sep='')
            return_dict[aver] = aver
        else:
            aver = 'Data_Consistency_Error'
            #print(aver)
            return_dict[aver] = aver

    except:
        time.sleep(11)          #Per a que les finestres estiguen obertes la mateixa estona i després puga classificar bé
        driver.quit()  # close window
        aver = 'SWW_Error'
        #print(aver)        # SWW stands for something went wrong
        return_dict[aver] = aver

#Treballem amb les dades de les últimes 10 ventes, com a màxim.

#Iniciem procés de multiprocecssing, necessito el multiprocessing module fora de la funció, de moment

def my_funtionauto(var, models, talles):
    import time
    modelitos = models
    tallitas = talles

    # Veig que en funció de quants elements tingui per evaluar, he de canviar el valor dels time sleeps.
    # Per a 4 elements, 5 seg i 3 seg em va be, llavors faré correr els elements de 4 en 4, al final faré el residu
    # Pot ser que això depenga del meu internet a casa, que és lento i carregar moltes pàgines a la vegada el satura
    # Provar a barcelona a vore com va sense i ajustar time sleeps

    resultats = []
    for j in range(0, len(modelitos) // var):            #SI faig for j in range(0, 2) la j valdrà 0 i 1, però segons la indexació de python està guay
            dic = {}                                #Creo un diccionari amb tots els processos
            #for i in range(0, 4):
                #dic['p{}'.format(i+4*j)] = multiprocessing.Process(target=my_function, args=(modelitos[i], tallitas[i], return_dict))

            #Canvio de bucle per si es crearen i s' inicialitzaren alhora
            #Accedeixo a cada element de el diccionari (cada búsqueda que faré)

                #UPDATE : HO FICO AL SEGÜENT BUCLE

            processes = []
            if __name__ == '__main__':                      #M'obliga windows i/o el mòdul
                manager = multiprocessing.Manager()
                return_dict = manager.dict()
                for i in range(0, var):
                    dic['p{}'.format(i + var * j)] = multiprocessing.Process(target=my_function, args=(modelitos[ i + var * j ], tallitas[ i + var * j ], return_dict))
                    elem = dic['p{}'.format(i+var*j)]
                    processes.append(elem)
                    elem.start()
                    time.sleep(12)
            for process in processes:
                process.join()              #Així, quan els 4 primers acaben, començaran els altres 4.
                resultats.append(return_dict.values())

    j = j + 1
    dic = {}
                                                                                                                       #mantinc el valor de la j anterior
    processes = []
    if __name__ == '__main__':  # M'obliga windows i/o el mòdul
        manager = multiprocessing.Manager()
        return_dict = manager.dict()
        for i in range(0, len(modelitos) % var):
            dic['p{}'.format(i + var * j)] = multiprocessing.Process(target=my_function, args=(modelitos[i + var * j ], tallitas[ i+ var * j ], return_dict))  # esta j es la j max, osigui la que surt del final del bucle anterior
            elem = dic['p{}'.format(i + var * j)]
            processes.append(elem)
            elem.start()
            time.sleep(12)

    for process in processes:
        process.join()
        resultats.append(return_dict.values())

    #count = 0
    #for listElem in resultats:
    #    count += len(listElem)
    #Troç de codi que a dia de avui no entenc xD

                              #Veig que depenenet de com es carregue la pàgina tinc diferents respostes, per exemple: ([[319.5, 309.6], [319.5, 309.6], [319.5, 309.6, 295.6, 440.9], [319.5, 309.6, 295.6, 440.9], [255.8]] per a var = 4
                                                #Busco un mètode alternatiu. Considero que mai tindré dos talles i models igual, o si els tinc, consideraré la quantitat
    resultatsfin = []

    #print(resultats)
    for i in range(0, len(modelitos)):
        for j in range(0, var):
            try:
                if not resultats[i][j] in resultatsfin:
                    resultatsfin.append(resultats[i][j])
                else:
                    pass
            except:
                pass

    #print(resultatsfin)





#            if len(resultats[i]) == var and resultats[i] == resultats[i+1]:
#               resultatsfin.append(resultats[i][i])
#           elif len(resultats[i]) == var and resultats[i] != resultats[i+1]:
#                #for j in range(0, len(resultats[i])):
#                resultatsfin.append(resultats[i][-1])
#                #break
#            elif len(resultats[i]) == len(modelitos) % var:
#                for j in range(0, len(resultats[i])):
#                    resultatsfin.append(resultats[i][j])
#                    break





        #else:
        #        resultatsfin.append('Error_Building_resultatsfin')

    #Si dono els resultats en € al excel se pasa en format text raro i no puc operar
    #resultatsend = [str(item) + '€' for item in resultatsfin]
    #return(resultatsend)
    return (resultatsfin)

models = ['adidas-yeezy-boost-350-v2-white-core-black-red', 'adidas-yeezy-boost-350-v2-white-core-black-red', 'adidas-yeezy-boost-350-v2-cloud-white', 'yeezy-slide-bone', 'adidas-yeezy-boost-350-v2-zyon', 'adidas-yeezy-boost-350-v2-ash-stone']
talles = [10.5, 6, 7, 7, 6.5, 5.5]

Finalresult = my_funtionauto(3, models, talles)     #Així no van apareixen els prints i ho guardo aquí!

def my_funexell(n):     #n es la columna a la que anirà
    today = date.today()
    d1 = today.strftime("%d/%m/%Y")

    #El problema de printejar més del compte no el té la funció! Està aquÍ!!
    # Si fico un else en literalment qualsevol altra cosa, me salten prints que no vull. Ho deixo així.

    if len(Finalresult) == len(models):
        Finalresult.insert(0, '')
        Finalresult.insert(0, d1)
        A = Finalresult
        print(A)
        df = pd.DataFrame({'Col A': A})
        book = load_workbook('stock.xlsx')
        writer = pd.ExcelWriter('stock.xlsx', engine='openpyxl')
        writer.book = book

        writer.sheets = dict((ws.title, ws) for ws in book.worksheets)

        df.to_excel(
            excel_writer=writer,
            sheet_name='Hoja1',
            columns=['Col A'],
            index=False,
            header=False,
            startrow=0,
            startcol=n)
        writer.save()
        writer.close()

        for element in A:
            print(element)

my_funexell(36)

#AL ENTRAR, FER RUN DIRECTAMENT
#AL CÓRRER EL CODI I SORTIR, SUMAR 2 AL INPUT DE my_funexell per a que no hi hagi esborrament/solapament de dades.















