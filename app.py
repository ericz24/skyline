#import py_avataaars
import random, logging, sys
import uvicorn

from newscatcherapi import NewsCatcherApiClient

from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.templating import Jinja2Templates
from starlette.config import Config
from starlette.staticfiles import StaticFiles
from starlette.responses import PlainTextResponse, JSONResponse
from starlette_exporter import PrometheusMiddleware, handle_metrics

import json
#from requests import get
from os import getenv, urandom, path, environ
#import aws
import urllib3

templates = Jinja2Templates(directory='templates')

#newscatcherapi = NewsCatcherApiClient(x_api_key=getenv('NEWS_API_KEY')) 
http = urllib3.PoolManager()

global_state = {
    "INITIALIZED": False
}

logging.basicConfig(stream=sys.stdout, level=eval('logging.' + getenv('LOG_LEVEL', 'INFO')))
logging.debug('Log level is set to DEBUG.')

def homepage(request):
    return PlainTextResponse('Hello, world!')

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

    print(json.dumps(allResponse, indent=2))
    return allResponse

def _setup(request):
    '''
    random.seed(str(request.url))
    if not path.isfile('avatar.png'):
        generate_avatar_image()
    if not path.isfile('./static/social.png'):
        generate_social_card('avatar.png')
    '''
    global_state["INITIALIZED"] = True

async def index(request):
    if request.method == "POST":
        form = await request.form()
        keywords = form["search"]
        #articles = newscatcherapi.get_search(q=keywords,
        #                                 lang='en',
        #                                 countries='US',
        #                                 page_size=100)
        #print(articles)

        response = http.request("GET", f"https://newsdata.io/api/1/news?apikey={getenv('NEWSDATA_API_KEY')}&q={keywords}&language=en")
        data_json=json.loads(response.data)
        return templates.TemplateResponse('index.html', {'request': request, 'articles':  data_json['results']})

    if "Go-http-client" in request.headers['user-agent']:
        # Filter out health checks from the load balancer
        return PlainTextResponse("healthy")
    if "curl" in request.headers['user-agent']:
        return templates.TemplateResponse('index.txt', {'request': request})
    else:
        if not global_state["INITIALIZED"]:
            _setup(request)
        #response = http.request("GET", f"https://newsdata.io/api/1/news?apikey={getenv('NEWSDATA_API_KEY')}&category=top,politics,sports,entertainment,technology&language=en&country=us")
        #data_json=json.loads(response.data)
        #print(json.dumps(data_json, indent=2))

        #results = data_json['results']
        results = _getResponse(f"https://newsdata.io/api/1/news?apikey={getenv('NEWSDATA_API_KEY')}&category=top&language=en&country=us")
        top_news = [result for result in results if result['category'][0] == 'top' and result['image_url']]
        results = _getResponse(f"https://newsdata.io/api/1/news?apikey={getenv('NEWSDATA_API_KEY')}&category=politics&language=en&country=us")
        politics_news = [result for result in results if result['category'][0] == 'politics' and result['image_url']]
        results = _getResponse(f"https://newsdata.io/api/1/news?apikey={getenv('NEWSDATA_API_KEY')}&category=sports&language=en&country=us")
        sports_news = [result for result in results if result['category'][0] == 'sports' and result['image_url']]
        results = _getResponse(f"https://newsdata.io/api/1/news?apikey={getenv('NEWSDATA_API_KEY')}&category=world&language=en")
        world_news = [result for result in results if result['category'][0] == 'world' and result['image_url']]
        results = _getResponse(f"https://newsdata.io/api/1/news?apikey={getenv('NEWSDATA_API_KEY')}&category=technology&language=en&country=us")
        technology_news = [result for result in results if result['category'][0] == 'technology' and result['image_url']]
        return templates.TemplateResponse('index.html', {'request': request, 'top_news': top_news, 'politics_news': politics_news, 'sports_news': sports_news, 'world_news': world_news, 'technology_news': technology_news})

def headers(request):
    return JSONResponse(dumps({k:v for k, v in request.headers.items()}))

routes = [
    Route('/', endpoint=index, methods=["GET", "POST"]),
    Route('/headers', endpoint=headers),
    Mount('/static', app=StaticFiles(directory='static'), name='static'),
]

app = Starlette(debug=True, routes=routes)
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)

config = Config()


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0",
                port=int(getenv('PORT', 8000)),
                log_level=getenv('LOG_LEVEL', "info"),
                debug=getenv('DEBUG', False),
                proxy_headers=True)
