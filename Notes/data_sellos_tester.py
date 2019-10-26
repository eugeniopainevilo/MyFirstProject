import requests
from bs4 import BeautifulSoup

#value='555101' # 2014
#value='432801' # 2013
#value='1341451' # 2018
#value='76336' # 2005
#value='398' # 2002
#value='71234' #2005
#value='120851' #2006
#value='198570' #2010
#value='254442' #genera error de sistema en la sec
#value='336445' #genera error de sistema en la sec
#value='815567'#genera error de sistema en la sec
#824467, 1001411, 1001415# mas errores
#value='2874' #2002
#value='161309' #2008
#value='198445' #2010
#value='845357' #2015
#value='199234' # 2010
#value='242303' # 2013
#value='914910' #2016
#value='1216033' #2017
value='575200' #2014
value='802450' # 2014
value='176450' #2009
value='482505'


with requests.Session() as s:
    req = s.get('http://wlhttp.sec.cl/ciige3/publico/consultas/consultaCertificacion.do')
    data = {"filtroId": value, 'filtroComuna': '0', 'filtroDireccion': '', 'accion': 'generarCertificado','idReporte': value}
    report_page = s.post('http://wlhttp.sec.cl/ciige3/publico/consultas/consultaCertificacion.do', data=data)
    soup = BeautifulSoup(report_page.text, 'html.parser')
        #print(soup)

    selloContainer = soup.find('td', width='58%', height="17")
    print("Sello : " + selloContainer.text.strip())
    if isinstance(selloContainer, type(None)):
        sello = "No Info"
        nDest=11
        nRut=16
        nEdif=9
    else:
        sello = selloContainer.text.strip()
        nDest=13
        nRut=18 
        nEdif=11

        
    print("Sello : " + sello)

    selloNumberContainer = soup.find_all('table', width = "99%", border ="0",cellspacing="2",cellpadding="2")[0]
    print("Numero de Sello : " + selloNumberContainer.text.strip())

    TipoDeProcesoContainer = soup.find_all('table', width = "100%", border ="0",cellspacing="2",cellpadding="2")[2]
    print("Tipo De Proceso : " + TipoDeProcesoContainer.text.strip())

    FechaPuestaSelloContainer =soup.find_all('table', width = "20%", border ="0",cellspacing="0",cellpadding="0")[0]
    print("Fecha Puesta Sello : " + FechaPuestaSelloContainer.text.strip())

    FechaVencimientoContainer =soup.find_all('table', width = "20%", border ="0",cellspacing="0",cellpadding="0")[1]
    print("Fecha Vencimiento : " + FechaVencimientoContainer.text.strip())
    
    DireccionContainer = soup.find_all('table', width="68%", border="0", cellpadding="2", cellspacing="2")[0]
    print("Direccion: " + DireccionContainer.text.strip())
    
    RutEmpresaContainer = soup.find_all('table', width="100%", border="0", cellpadding="2", cellspacing="2")[20] #16 anormal, 18 normal, 20 en algarrobo
    print('Rut Empresa: ' + RutEmpresaContainer.text.strip())
    
    TipoEdificioContainer = soup.find_all('table', width="100%", border="0", cellpadding="2", cellspacing="2")[11]
    print('Tipo Edificio: ' + TipoEdificioContainer.text.strip())
    
    DestinoContainer = soup.find_all('table', width="100%", border="0", cellpadding="2", cellspacing="2")[13] #9 para el anormal y 13 para normal
    print('Destino: ' + DestinoContainer.text.strip())

