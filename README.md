# webscraping-pucp
Web scraping de sitios web con python3 y django2

1ra parte: Análisis de Urls, Ok

2da parte: Descarga de datos, Ok

Nota: Se le recomienda trabajar con un entorno virtual, una vez activado ejecutar los siguientes procedimientos


>> git clone https://github.com/alejandrohdo/webscraping-pucp.git

>> cd webscraping-pucp

>> pip3 install -r requirements.txt

>> ./manage.py migrate

>> ./manage.py createsuperuser

>> ./manage.py runserver

http://localhost:8000/

visualización de información: http://localhost:8000/admin/scraping/noticia/

Instalación de NLP en newspaper, para determinar las palabras claves, en el terminal ejecutar:

>> python

>> import nltk

>> nltk.download('popular')

Presentación:https://docs.google.com/presentation/d/1V7BJoiIeeH6IQH0lTEZTTrE6ryGJLKu_ohmQRbQphmg/edit?usp=sharing

Próximo taller: Integracion con celery!
