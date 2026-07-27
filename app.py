from fastapi import FastAPI, UploadFile, Request, HTTPException
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates

from fec_parser.computations import FECComputation
from fec_parser.errors import BadFECFileError
from fec_parser.indicators import FECIndicators
from fec_parser.parser import FECParser
from fec_parser.version import get_pcg_config

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse("favicon.ico")

@app.get('/fec_exemple.txt', include_in_schema=False)
async def fec_exemple():
    return FileResponse("fec_exemple.txt")

@app.get('/etcld-logo.svg', include_in_schema=False)
async def favicon():
    return FileResponse("etcld-logo.svg")

@app.post("/upload/")
async def create_upload_file(file: UploadFile):
    try:
        parser = FECParser.from_bytesio(file.file)
        parser.parse()
        ecritures = list(parser.get_ecritures())
    except BadFECFileError:
        raise HTTPException(status_code=400)

    config = get_pcg_config(ecritures=ecritures)
    computations = FECComputation(ecritures, pc_definition_filepath="definition_file.csv")
    indicators = FECIndicators(ecritures, config)
    return {
        "indicateurs": indicators.compute_indicateurs(),
        "compte_resultat": computations.compute_compte_resultat(),
    }

@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
