#import py_avataaars
import random, logging, sys
import uvicorn

#from newscatcherapi import NewsCatcherApiClient

from starlette.routing import Route, Mount
from starlette_exporter import PrometheusMiddleware, handle_metrics

from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import json
#from requests import get
from os import getenv, urandom, path, environ
#import aws
import urllib3

templates = Jinja2Templates(directory='templates')

#newscatcherapi = NewsCatcherApiClient(x_api_key=getenv('NEWS_API_KEY')) 
http = urllib3.PoolManager()

logging.basicConfig(stream=sys.stdout, level=eval('logging.' + getenv('LOG_LEVEL', 'INFO')))
logging.debug('Log level is set to DEBUG.')

def _getResponse(url, pagination = False):
    allResponse = []
    page = ""
    pagedUrl = url
    while True:

        if page:
            pagedUrl = url + f"&page={page}"
        response = http.request("GET", pagedUrl)
        data_json=json.loads(response.data)
        results = data_json['results']

        allResponse = allResponse + results

        if pagination:

            page = data_json['nextPage']

        if not page:
            break

    #print(json.dumps(allResponse, indent=2))
    return allResponse

async def search(request):
    if request.method == "POST":
        form = await request.form()
        keywords = form["search"]

        response = http.request("GET", f"https://newsdata.io/api/1/news?apikey={getenv('NEWSDATA_API_KEY')}&q={keywords}&language=en")
        data_json=json.loads(response.data)
        logging.debug('keywords: ' + keywords)
        return templates.TemplateResponse('search.html', {'request': request, 'news_returned':  data_json['results'], 'keywords': keywords})
    else:
        return templates.TemplateResponse('search.html', {'request': request, 'news_returned':  [], 'keywords': ''})

async def index(request):
    if "Go-http-client" in request.headers['user-agent']:
        # Filter out health checks from the load balancer
        return PlainTextResponse("healthy")
    else:
        #response = http.request("GET", f"https://newsdata.io/api/1/news?apikey={getenv('NEWSDATA_API_KEY')}&category=top,politics,sports,entertainment,technology&language=en&country=us")
        #data_json=json.loads(response.data)
        #print(json.dumps(data_json, indent=2))

        #results = data_json['results']
        results = _getResponse(f"https://newsdata.io/api/1/news?apikey={getenv('NEWSDATA_API_KEY')}&category=top&language=en&country=us&image=1")
        top_news = [result for result in results if result['category'][0] == 'top' and result['image_url']]
        results = _getResponse(f"https://newsdata.io/api/1/news?apikey={getenv('NEWSDATA_API_KEY')}&category=politics&language=en&country=us&image=1")
        politics_news = [result for result in results if result['category'][0] == 'politics' and result['image_url']]
        results = _getResponse(f"https://newsdata.io/api/1/news?apikey={getenv('NEWSDATA_API_KEY')}&category=sports&language=en&country=us&image=1")
        sports_news = [result for result in results if result['category'][0] == 'sports' and result['image_url']]
        results = _getResponse(f"https://newsdata.io/api/1/news?apikey={getenv('NEWSDATA_API_KEY')}&category=world&language=en&image=1")
        world_news = [result for result in results if result['category'][0] == 'world' and result['image_url']]
        results = _getResponse(f"https://newsdata.io/api/1/news?apikey={getenv('NEWSDATA_API_KEY')}&category=technology&language=en&country=us&image=1")
        technology_news = [result for result in results if result['category'][0] == 'technology' and result['image_url']]
        return templates.TemplateResponse('index.html', {'request': request, 'top_news': top_news, 'politics_news': politics_news, 'sports_news': sports_news, 'world_news': world_news, 'technology_news': technology_news})

def headers(request):
    return JSONResponse(dumps({k:v for k, v in request.headers.items()}))

routes = [
    Route('/', endpoint=index),
    Route('/index.html', endpoint=index),
    Route('/search', endpoint=search, methods=["GET", "POST"]),
    Route('/headers', endpoint=headers),
    Mount('/static', app=StaticFiles(directory='static'), name='static'),
]

app = FastAPI(routes=routes)
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0",
                port=int(getenv('PORT', 8000)),
                log_level=getenv('LOG_LEVEL', "info"),
                debug=getenv('DEBUG', False),
                proxy_headers=True)
