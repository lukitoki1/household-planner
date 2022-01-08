from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import os
import six
from google.cloud import translate_v2 as translate


app = FastAPI()
origins = ["*"]
os.environ['GOOGLE_APPLICATION_CREDENTIALS']='gtranslate-key.json'

app.add_middleware(GZipMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

lang_list = []

@app.on_event('startup')
async def startup_event():
    translate_client = translate.Client()
    results = translate_client.get_languages()
    for lang in results:
        lang_list.append(lang['language'])


@app.get("/api/translation")
async def root(lang: str, text: str):
    translation = get_translation(lang,text)
    if translation is None:
        raise HTTPException(status_code=404, detail='Translation failed')
    if translation is -1:
        raise HTTPException(status_code=404, detail='Wrong target language')
    return translation

def get_translation(lang: str, text: str):
    translate_client = translate.Client()
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")
    if lang not in lang_list:
        return -1
    result = translate_client.translate(text, target_language=lang)
    return result['translatedText']