import requests
from bs4 import BeautifulSoup
#extraer los id de la base de datos
import sqlite3
conexion=sqlite3.connect("Data_Sec.db")
cursor=conexion.cursor()

#id_list=cursor.execute("SELECT id_proceso FROM id_list WHERE id_comuna = '13-5-2'").fetchall() # una comuna en particular
id_list=cursor.execute("SELECT id_list.id_proceso FROM id_list LEFT JOIN data_sellos ON id_list.id_proceso = data_sellos.id_proceso WHERE data_sellos.id_proceso IS NULL").fetchall() # id procesos sin data aun
print(str(len(id_list))+" id imported")
conexion.close()

#preparo las cosas para buscar la data
n_saving = 50 #parámetro para guardar y no perder avance
data_list=[] 
counter=0 #agregarle +1 cuando re-inicie manualmente
for element in id_list[:]:
    with requests.Session() as s:
        try:
            req = s.get('http://wlhttp.sec.cl/ciige3/publico/consultas/consultaCertificacion.do')
            data = {"filtroId": element[0], 'filtroComuna': '0', 'filtroDireccion': '', 'accion': 'generarCertificado','idReporte': element[0]}
            report_page = s.post('http://wlhttp.sec.cl/ciige3/publico/consultas/consultaCertificacion.do', data=data)
            soup = BeautifulSoup(report_page.text, 'html.parser')
        except:
            try:
                print("whoops! we've got disconnected. Let's try again")
                req = s.get('http://wlhttp.sec.cl/ciige3/publico/consultas/consultaCertificacion.do')
                data = {"filtroId": element[0], 'filtroComuna': '0', 'filtroDireccion': '', 'accion': 'generarCertificado','idReporte': element[0]}
                report_page = s.post('http://wlhttp.sec.cl/ciige3/publico/consultas/consultaCertificacion.do', data=data)
                soup = BeautifulSoup(report_page.text, 'html.parser')
            except:
                print("whoops! we've got disconnected for 2nd time in a row. Let's try again")
                req = s.get('http://wlhttp.sec.cl/ciige3/publico/consultas/consultaCertificacion.do')
                data = {"filtroId": element[0], 'filtroComuna': '0', 'filtroDireccion': '', 'accion': 'generarCertificado','idReporte': element[0]}
                report_page = s.post('http://wlhttp.sec.cl/ciige3/publico/consultas/consultaCertificacion.do', data=data)
                soup = BeautifulSoup(report_page.text, 'html.parser')
            
    try:

        FechaPuestaSelloContainer =soup.find_all('table', width = "20%", border ="0",cellspacing="0",cellpadding="0")[0] #la fecha me da los parametros de tipoedif, destino y rut
        FechaPuesta = FechaPuestaSelloContainer.text.strip()
        year=int(FechaPuesta[6:])

        if year >= 2010: #establezco las condiciones regulares sobre 2010
            nRut=18
            nEdif=11
            nDest=13
            vw='100%'
        else:
            nRut=20
            nEdif=11
            nDest=0
            vw='98%'

        selloContainer = soup.find('td', width='58%', height="17")
        #print("Sello : " + selloContainer.text.strip())
        if isinstance(selloContainer, type(None)):
            sello = "No Info"
            nDest=11
            nRut=16
            nEdif=9
        else:
            sello = selloContainer.text.strip()

        selloNumberContainer = soup.find_all('table', width = "99%", border ="0",cellspacing="2",cellpadding="2")[0]
        #print("Numero de Sello : " + selloNumberContainer.text.strip())
        selloNumber = selloNumberContainer.text.strip()

        FechaPuestaSelloContainer =soup.find_all('table', width = "20%", border ="0",cellspacing="0",cellpadding="0")[0]
        #print("Fecha Puesta Sello : " + FechaPuestaSelloContainer.text.strip())
        FechaPuesta = FechaPuestaSelloContainer.text.strip()

        FechaVencimientoContainer =soup.find_all('table', width = "20%", border ="0",cellspacing="0",cellpadding="0")[1]
        #print("Fecha Vencimiento : " + FechaVencimientoContainer.text.strip())
        FechaVenS=FechaVencimientoContainer.text.strip()

        RutEmpresaContainer = soup.find_all('table', width="100%", border="0", cellpadding="2", cellspacing="2")[nRut]
        #print('Rut Empresa: ' + RutEmpresaContainer.text.strip())
        RutEmp = RutEmpresaContainer.text.strip()

        TipoEdificioContainer = soup.find_all('table', width="100%", border="0", cellpadding="2", cellspacing="2")[nEdif]
        #print('Tipo Edificio: ' + TipoEdificioContainer.text.strip())
        TipoEdif = TipoEdificioContainer.text.strip()

        DestinoContainer = soup.find_all('table', width=vw, border="0", cellpadding="2", cellspacing="2")[nDest]
        #print('Destino: ' + DestinoContainer.text.strip())
        Destino = DestinoContainer.text.strip()

        DireccionContainer = soup.find_all('table', width="68%", border="0", cellpadding="2", cellspacing="2")[0]
        Direccion=DireccionContainer.text.strip()
        #print("Direccion: " + DireccionContainer.text.strip())
        
        print(" id: " + str(element[0])+' Rut Empresa: ' + RutEmp + " (No " + str(counter+1)+") " + TipoEdif+ " - " + Destino+" fecha p: "+ FechaPuesta)

        data_list.append([element[0], sello, selloNumber, FechaPuesta, FechaVenS, RutEmp, TipoEdif, Destino, Direccion])
        counter=counter+1
    except:
        print("whoops! that one didn't work. Let's try the next one")
        data_list.append([element[0], 'SIN INFO', 'SIN INFO', 'SIN INFO', 'SIN INFO', 'SIN INFO', 'SIN INFO', 'SIN INFO','SIN INFO'])
        counter=counter+1
    
    #print(len(data_list))
    if (counter % n_saving == 0): #inserto en la bd cada cierta cantidad
        conexion=sqlite3.connect("Data_Sec.db")
        cursor=conexion.cursor()

        cursor.executemany("INSERT INTO data_sellos VALUES (?,?,?,?,?,?,?,?,?)", data_list)

        conexion.commit()
        conexion.close()
        print('the data was insterted! '+ str(round(100*counter/len(id_list),2))+'%')
        data_list=[]

#inserto para los valores remanentes
conexion=sqlite3.connect("Data_Sec.db")
cursor=conexion.cursor()

cursor.executemany("INSERT INTO data_sellos VALUES (?,?,?,?,?,?,?,?,?)", data_list)

conexion.commit()
conexion.close()

print("It's done! you got "+(str(len(data_list)))+' elements inserted')