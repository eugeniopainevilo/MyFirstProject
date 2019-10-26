import requests
from bs4 import BeautifulSoup
import pandas as pd
url = "http://wlhttp.sec.cl/ciige3/publico/consultas/consultaCertificacion.do"
#extraer los id comuna de la base de datos
import sqlite3
conexion=sqlite3.connect("Data_Sec.db")
cursor=conexion.cursor()

comunas=cursor.execute("SELECT DISTINCT comunas.id_comuna FROM comunas LEFT JOIN id_list ON id_list.id_comuna = comunas.id_comuna WHERE id_list.id_comuna IS NULL AND comunas.region = 'V Región'").fetchall() # extrae las comunas que aun no tienen id_proceso
#comunas=cursor.execute("SELECT id_comuna FROM comunas WHERE region = 'VI Región'").fetchall() # para hacerlo automatico debo cambiar a comuna[0]
print(str(len(comunas))+" comuna imported")
files=0
file_names=""
conexion.close()
#rangos no toman el limite superior
for comuna in comunas[:]:
    data = {"filtroId": '', 'filtroComuna': comuna[0], 'filtroDireccion': '', 'accion': 'buscar', 'idReporte': ''}
    page = requests.post(url, data)
    soup = BeautifulSoup(page.text, 'html.parser')

    id_list=[]

    pagenumberContainer =soup.find('span', class_="texto_links")
    endPageNumber = pagenumberContainer.text.split('de')[1].strip() #este valor puede causar problemas sobre 1000 (1,600 no es int)
    print("comuna: "+ comuna[0]+ ", paginas: " + endPageNumber)


    pagenumber = 1 #parte de 1
    contador=1
    while pagenumber <= int(endPageNumber):
        s = requests.Session()
        req = s.get(url)
        pagedata = {"filtroId": '', 'filtroComuna': comuna[0], 'filtroDireccion': '', 'accion': 'buscar', 'idReporte': '',
                    'd-16544-p': pagenumber}

        try:
            report_page = s.post(url, data=pagedata)
            report_soup = BeautifulSoup(report_page.text, 'html.parser')
            container = report_soup.find_all('td', style="width: 80px;")
        except:
            print('whoops! we have got disconnected, lets try again')
            try:
                report_page = s.post(url, data=pagedata)
                report_soup = BeautifulSoup(report_page.text, 'html.parser')
                container = report_soup.find_all('td', style="width: 80px;")
            except:
                print('whoops! we have got disconnected for 2nd time in a row, lets try again')
                report_page = s.post(url, data=pagedata)
                report_soup = BeautifulSoup(report_page.text, 'html.parser')
                container = report_soup.find_all('td', style="width: 80px;")

        index = 0
        while index < len(container):
            #print(container[index].text.strip() + " No: " + str(contador))
            id_list.append([container[index].text.strip(), comuna[0], pagenumber])
            index = index + 2
            contador = contador+1

        print("pag: " + str(pagenumber) + ", avance: " +str(round(100*pagenumber/int(endPageNumber),1))+"%")
        pagenumber = pagenumber + 1
            


    #importing to Excel
    df=pd.DataFrame(id_list)

    writer = pd.ExcelWriter(comuna[0] + '.xlsx')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    print("it's done! you've got "+(str(contador))+' rows scraped and saved in the file:' + comuna[0] + '.xlsx')
    files=files+1
    file_names=file_names+", "+comuna[0]+'.xlsx'
    
print('Finish: '+ str(files) + " files generated: "+ file_names)