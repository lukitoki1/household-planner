from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from translation import get_translation
app = FastAPI()

origins = ["*"]

app.add_middleware(GZipMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/translation")
async def root(lang: str, text: str):
    translation = get_translation(lang,text)
    if translation is None:
        raise HTTPException(status_code=404, detail='Translation failed')
    return translation