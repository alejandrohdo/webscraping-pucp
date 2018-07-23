from django.shortcuts import render
from django.views.generic import ListView, TemplateView
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import json
from .get_user_agent import get_user_agents
from .get_rotation_proxy import get_proxies
import random
import re
from requests.exceptions import (ReadTimeout, ReadTimeout,
                                 Timeout, ConnectTimeout, ConnectionError, ProxyError)
from newspaper import Article, Config
from newspaper.article import ArticleException
from .models import Noticia
proxys = get_proxies()
proxy = proxys[random.randrange(0, len(proxys))]
agente_usuario = random.choice(get_user_agents())
count_request = 0
requests_attempts = 0
arrayOnlyUrlHost = []


def correctorUrl(urlSite, urlChildren):

    if(urlChildren == None):
        return False
    urlChildren = re.sub('<[^<]+?>', '', urlChildren)
    urlChildren = urlChildren.strip()
    # es importante para las suburl
    if urlSite[len(urlSite)-1] == "/":
        urlSite = urlSite[0:(len(urlSite)-1)]

    urlResult = urljoin(urlSite, urlChildren)
    urlResult = urlResult.split('#')[0]
    # verificamos si algun url al final contiene una de estas extensiones,
    # no lo consideramos, mientras que la url al menos contenga un "/"
    if urlResult.find('/') != -1:
        valor = (urlResult.rsplit('/', 1)[1])
        valor1 = valor.split('.')
        if any(c in valor1 for c in ("png", "pdf", "jpg",
                                     "jpeg", "gif", 'ico',
                                     'psd', 'doc', 'docx',
                                     'xls', 'exe', 'bmp', 'mov', 'avi'
                                     'otf', 'ttf', 'zap', 'zip', 'mp3',
                                     'wav', 'mp4', 'movie', 'mpg', 'iso'
                                     'rar', 'cdr', 'txt', 'ppt', 'pptx',
                                     'csv', 'css', 'json', 'java', 'swf')):
            return False
    # si en caso se encuentra un pdf tipo:
    # https://www.telefonica.com.pe/documents/2015.pdf/69f20
    if len(urlResult.split('.pdf')) > 1 or len(urlResult.split('.PDF')) > 1:
        return False
    return urlResult


def onlyUrlHost(urlSite, urlChildren):
    if(urlChildren != False and urlSite != False):
        a = urlparse(urlSite)
        # print ("VALOR DE A:", a)
        b = urlparse(urlChildren)
        # print ("VALOR DE B:", b)
        if(a.netloc != '' and b.netloc != '' and a.netloc == b.netloc):
            return urlChildren
    return False


def retry_request(url):
    '''
    Método que nos permite cambiar de Proxy
    en caso que el tiempo de espera supero 10s
    estado: False, siginifica que obtuvo respuesta,
    caso contrario volvera a cambiar -- ∞∞∞.
    return List : Data, estado: [proxy1, proxyt2....], False o True
    '''
    estado = True
    global proxys
    global proxy
    global agente_usuario
    global requests_attempts
    proxys = get_proxies()
    proxy = proxys[random.randrange(0, len(proxys))]
    agente_usuario = random.choice(get_user_agents())
    proxies = {
        "http": 'http://' + proxy,
        "https": 'https://' + proxy
    }
    try:
        # con allow_redirects=False, evitamos redireccionamiento como: A -->B--><--C
        r = requests.get(url,
                         headers={'User-Agent': agente_usuario},
                         proxies=proxies,
                         timeout=12,
                         allow_redirects=False,
                         verify=False
                         )
        # por Ahora la respuesta en un PDF lo obiamos
        if r.headers.get('Content-Type') == 'application/pdf':
            r = None
        estado = False
        data = {'r': r, 'estado': estado}
        return data
    except Exception as e:
        requests_attempts += 1
        data = {'r': '', 'estado': estado}
        return data


def getUrls(url, save=False):
    url_padre = url
    arrayOnlyUrlHost = []
    global proxys
    global proxy
    global agente_usuario
    global count_request
    global requests_attempts
    if count_request >= 150:
        # en cada 150 peticiones cambiamos de Proxy y agente de Usuario
        proxys = get_rotation_proxy.get_proxies()
        proxy = proxys[random.randrange(0, len(proxys))]
        agente_usuario = random.choice(get_user_agents())
        count_request = 0
    proxies = {
        "http": 'http://' + proxy
    }
    try:
        r = requests.get(url,
                         headers={'User-Agent': agente_usuario},
                         proxies=proxies,
                         timeout=12,
                         allow_redirects=False,
                         verify=False)
        # si por por ABO la url es un pdf, lo obiamos
        if r.headers.get('Content-Type') == 'application/pdf':
            r = None
        count_request += 1
    except (ReadTimeout, Timeout, ConnectTimeout,
            ConnectionError, ProxyError) as e:
        print("Cambiando de proxy---------------->:", str(e))
        retry_value = retry_request(url)
        while retry_value['estado']:
            retry_value = retry_request(url)
            if retry_value['estado'] and requests_attempts <= 4:
                retry_value = retry_request(url)
            else:
                requests_attempts = 0
                break
        r = retry_value.get('r', None)
        if r:
            if r.headers.get('Content-Type') == 'application/pdf':
                r = None
    except Exception as e1:
        r = None
        raise e1
    if r:
        # almacenarlas en solr
        # preguntar si yas las tenermos almacendas
        if(onlyUrlHost(r.url, url) == False):
            return False
        soup = BeautifulSoup(r.text, 'lxml')
        tags = soup.find_all('a')
        arrayOtherUrlHost = []
        for tag in tags:
            urlResult = correctorUrl(r.url, tag.get('href'))
            if(urlResult == False):
                continue
            resultOnlyUrl = onlyUrlHost(r.url, urlResult)
            if(resultOnlyUrl == False):
                arrayOtherUrlHost.append(urlResult)
            else:
                if(urlResult not in arrayOnlyUrlHost):
                    arrayOnlyUrlHost.append(urlResult)
    return arrayOnlyUrlHost

# configuracion para hacer peticiones personalizadas


def config_newspaper():
    ''''
    proxy : random
    languaje : es,
    user_agent: random
    return Config[]
    '''
    config = Config()
    config.browser_user_agent = random.choice(get_user_agents())
    proxys = get_proxies()
    if len(proxys) <= 0:
        proxy = proxys[random.randrange(0, len(proxys) + 1)]
    else:
        proxy = proxys[random.randrange(0, len(proxys))]
    proxies = {"http": 'http://' + proxy}
    config.proxies = proxies
    config.language = 'es'
    return config


def save_url(urls):
    estado = False
    global requests_attempts
    new_config = config_newspaper()
    for url in urls:
        print('DESCARGANDO URL:', url)
        # Insertart Article
        p, created = Noticia.objects.get_or_create(url = url)
        try:
            if created:
               article = Article(url=url, config=new_config)
               article.download()
               article.parse()
               article.nlp()
               if article.text:
                    requests_attempts = 0
               else:
                    article = None
               if article:
               # get_or_create() a Article with similar first url.
                    if article.publish_date:
                        fecha_publicacion = (article.publish_date).strftime(
                                '%Y-%m-%dT%H:%M:%SZ')
                    else:
                        fecha_publicacion = None
                    p.titulo = article.title
                    p.resumen = article.summary
                    p.autor = article.authors
                    p.fecha_publicacion = fecha_publicacion
                    p.contenido = article.text
                    p.palabras_clave = article.keywords
                    p.imagen_destacada = article.top_image
                    p.video = article.movies
                    p.save()
                    print ('Se ha guardado la Url:', article.url)

            else:
               print ('Ya exite la Url:', url)
        except Exception as e:
            print("ERROR, POSIBLEMENTE LA PAGINA NO SE PUEDE ACCEDER:", e)
            print("CAMBIANDO DE PROXY Y AGENTE DE USUARIO----->:",
                  requests_attempts, " Intentos")
            retry_value = retry_request(url)
            while retry_value['estado']:
                retry_value = retry_request(url)
                if retry_value['estado'] and requests_attempts <= 2:
                    retry_value = retry_request(url)
                else:
                    requests_attempts = 0
                    break
            article = retry_value.get('article', None)
            if article:
                # get_or_create() a Article with similar first url.
                if article.publish_date:
                    fecha_publicacion = (article.publish_date).strftime(
                            '%Y-%m-%dT%H:%M:%SZ')
                else:
                    fecha_publicacion = None
                p.titulo = article.title
                p.resumen = article.summary
                p.autor = article.authors
                p.fecha_publicacion = fecha_publicacion
                p.contenido = article.text
                p.palabras_clave = article.keywords
                p.imagen_destacada = article.top_image
                p.video = article.movies
                p.save()
                print ('Se ha guardado la Url, en reintento:', article.url)
        estado = True
    return estado

# Create your views here.


class Index(TemplateView):
    template_name = 'scraping/index.html'


def procesar_url(request):
    if request.method == 'POST':
        result_url = getUrls(request.POST['dominio'])
        print('URLS ENCONTRADOS', result_url)
        print('CANTIDAD DE URL ENCONTRADOS-->', len(result_url))
        print('INSERTANDO URLS A LA BASE DE DATOS')
        estatus_save = save_url(result_url)
        if estatus_save:
            print('Ha terminado de Instar todo con exito..!')
        else:
            print('Es posible que se haya generado error al guardar urls')

        return render(request, 'scraping/index.html', {'urls': result_url})
