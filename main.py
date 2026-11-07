# for generating cookie hashes
import hashlib

# for securely loading secrets
from dotenv import load_dotenv, dotenv_values
import os

# for comparing secrets
import secrets

# data validation
from typing import Annotated
from datamodels import *

# backend
from fastapi import FastAPI, HTTPException, Depends, Cookie, Form, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from contextlib import asynccontextmanager

# frontend
from fastapi.staticfiles import StaticFiles

# database
import asyncpg
from datetime import datetime, timezone, timedelta

# for templating the long forms
from fastapi.templating import Jinja2Templates

# for sending email
from email.message import EmailMessage
import smtplib, ssl


from content.pages import pages # einladen, einloggen, einreichen
from content.scales import scales # gen_vals, adhs_vals, gen_scale, adhs_scale



# for cookie hashes


ADM_MAIL = "it.matthess@t-online.de"
MAILOUT="securesmtp.t-online.de"

# secrets
load_dotenv()
ADM_KEY=os.getenv('ADM_KEY').encode()
ADM_MAIL_KEY=os.getenv('ADM_MAIL_KEY')
COOKIES = {"token","session"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    # setup
    cfg = dotenv_values(".env")
    app.state.pool = await asyncpg.create_pool(
            dsn=str(cfg["DB_URL"]),
            min_size=0,
            max_size=20
            )
    yield
    # cleanup
    await app.state.pool.close()
async def getcon(request: Request):
    async with request.app.state.pool.acquire() as c:
        yield c
app = FastAPI(lifespan=lifespan)


# FRONTEND #



@app.get("/{name}")
def frontend(name:str,token: str|None = None, session: Annotated[str,Cookie()]=None, c: syncpg.Connection = Depends(getcon)):
    
    if name not in pages:
        raise HTTPException(status_code=400, detail="Ups. Diese Seite existiert nicht. Falls Sie eingeloogt sind, gehen Sie bitte zu ../einreichen.")
    
    if (name == "einreichen") and (session == None or not session_valid(session)):
            raise HTTPException(status_code=401)
    if token:
        name="".join([name,"&token=",token])
    return RedirectResponse("/pages/page.html?name="+name)

# front end will render the default page with info from /api/get frontend, request services at /api/post backend, and reroute. 
# only the route from /einloggen to /einreichen needs to carry a cookie ( called 'session' )

#@app.get("/pages/page.html")
#def template(session: Annotated[str|None,Cookie()]=None):



# BACKEND #


@app.get("/api/get/{name}")
def getpageinfo(name: str):
    if name not in pages:
        raise HTTPException(status_code=400)
    return pages[name]



@app.post("/api/post/einladen", status_code=200)
async def invite(data: Annotated[Einladung, Form()], c: syncpg.Connection = Depends(getcon)):

    pw = data.pw.get_secret_value().encode()
    if not secrets.compare_digest(pw,ADM_KEY): raise HTTPException(status_code=401, detail="admin auth failed.")

    email = data.email
    vn = data.vornamen
    nn = data.nachnamen

    patient = await get_patient(email, c) 
    pid = patient.get("id")
    if pid == None:
        pid = await new_patient(vn, nn, email, c)
    else: 
        if not await name_unique():
            raise HTTPSException(status_code=402, detail="patient record with same name and different email exists. please check manually.")
        if not patient["vornamen"] == vn or not patient["nachnamen"] == nn:
            raise HTTPSException(status_code=402, detail="patient name does not match with its email record. email cannot be used twice.")
    
    if await has_cookie(c,pid,'session') != None: 
        raise HTTPException(status_code=403, detail="users session exists already")
    if (tokenhash := await has_cookie(c,pid,'token')) != None: 
        await consume_cookie(c,tokenhash,'token')

    token = await new_cookie(c,pid,'token')
    link = f"localhost:8000/einloggen?token={token}"
    await invite_patient(vn, nn, link, email) 
    return { "ok":1 }




@app.post("/api/post/einloggen", status_code=200)
async def startsession(data: Annotated[Login, Form()], response: Response, c: syncpg.Connection = Depends(getcon)):

    token = data.token.get_secret_value()
    if not await cookie_valid(c,token,'token'):
        raise HTTPException(status_code=403,detail="token does not exist or has expired! please request new.")

    pid = await consume_cookie(c,hash_cookie(token),'token')
    session = await new_cookie(c,pid,'session')
            
    response.set_cookie (
            "session", 
            session, 
            httponly=True, # to prevent javascript to read the cookie
            secure=True, # https only :)
            samesite="lax" # to prevent CSRF. cookie is sent over only for top level GET navigations 
            )
    return { "ok":1 }




@app.post("/api/post/einreichen", status_code=200)
async def submit(data: Annotated[Selbsttest, Form()], response: Response, session: Annotated[str | None, Cookie()], c: syncpg.Connection = Depends(getcon)):
    
    if session == None or not cookie_valid(c,session,"session"):
        raise HTTPException(status_code=401, detail="Sie sind nicht eingeloggt! keine Sitzung oder Sitzung abgelaufen.")

    patient = await get_session_patient(c,session)

    answers = data.model_dump()
    result = compute_result(answers)

    tid = await new_test(patient["id"], result,c)
    for (qid,answer) in answers.items():
        aid = await new_answer(qid,answer,tid,c)
    
    await consume_cookie(c,hash_cookie(session),'session')
    await answer_patient(patient["vornamen"],patient["nachnamen"],result,patient["email"])
    response.delete_cookie(key=session, secure=True)

    return { "ok":1 }




# USER #

async def get_patient(email: str, c: syncpg.Connection) -> dict[str,int|str]:
    patient = await c.fetch("SELECT id, vornamen, nachnamen FROM Patient WHERE email = ($1);",email)
    return dict(patient)

async def new_patient(vn: str, nn: str, email: str, c: syncpg.Connection) -> int:
    return await c.fetchval("INSERT INTO Patient (vornamen, nachnamen, email) VALUES ($1, $2, $3) RETURNING id;",
            vn, nn, email)

async def name_unique(vn: str, nn: str, c: syncpg.Connection) -> bool:
        patients = await c.fetch("SELECT * from Patient where nachnamen = ($1) and vornamen = ($2)", vn, nn)
        patients = [dict(row) for row in patients]
        if patients != []:
            return False
        return True




# COOKIES # 


async def has_cookie(c: syncpg.Connection, pid: str, cookietype:str) -> str:
    if cookietype not in COOKIES:
        raise ValueError("!")
    query = f'SELECT c.hash FROM {cookietype} c JOIN Patient p ON c.patient_id = p.id WHERE c.expires_at > now() AND p.id = ($1);'
    return await c.fetchval(query,pid)


async def cookie_valid(c: syncpg.Connection, cookie: Annotated[str, Cookie()]| str) -> bool:
    if cookietype not in COOKIES:
        raise ValueError("!")
    cookiehash = hash_cookie(cookie)
    query = f"SELECT hash FROM {cookietype} WHERE hash = ($1) and s.expires_at > now();",
    hashs = await c.fetchval(query, cookiehash)
    hashes = list(hashs)
    if hashes != []:
        return True
    return False


async def new_cookie(c: syncpg.Connection, pid : str, cookietype:str) -> str:    
    # return a token or session cookie. NOT hashed
    # checks if cookie exists. :)
    if cookietype not in COOKIES:
        raise ValueError("!")

    if cookietype == "token":
        token = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(days=14)
        hash = hash_cookie(token)
    else:
        session = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(hours=2)
        hash = hash_cookie(session)
    query=f'INSERT INTO {cookietype} (hash, patient_id, expires_at) VALUES ($1,$2,$3);'
    await c.execute(query,hash, int(pid), expires)
    if cookietype == "token":
        return token
    return session


async def consume_cookie(c : syncpg.Connection,  cookiehash:str, cookietype:str):
    # gets a cookiehash and deletes it from database. this is safer because querying existence internally will return a hash and only a hash.
    if cookietype not in COOKIES:
        raise ValueError("!")
    query = f'DELETE FROM "{cookietype}" WHERE hash = ($1)'
    await c.execute(query,cookiehash)


async def get_session_patient(c : syncpg.Connection, cookie: Annotated[str | None, Cookie()])-> dict:
    if cookie is None:
        raise HTTPException(status_code=401, detail="no access without session cookie")

    hashcookie = hash_cookie(cookie)

    query=f'SELECT * FROM {cookietype} c JOIN Patient p ON c.patient_id = p.id WHERE c.hash = ($1) and c.expires_at > now();'

    row = await c.fetchrow(query, hashcookie)

    if row is None: 
        raise HTTPException(status_code=401,detail="could not fetch session info using cookie")

    return dict(row)



def hash_cookie(cookie: str) -> str:
    # this transforms a cookie into a hash of 256 digits, 64 bits
    return hashlib.sha256(cookie.encode()).hexdigest()






# EMAIL #


async def send_email(email:str, subject:str, text:str):
    sslctx = ssl.create_default_context()
    msg= EmailMessage()
    msg["From"] = ADM_MAIL
    msg["To"] = email
    msg["Subject"] = subject
    msg.set_content(text)

    with smtplib.SMTP_SSL(MAILOUT, 465, context=sslctx, timeout=10) as server:
        server.login(ADM_MAIL,ADM_MAIL_KEY)
        server.send_message(msg)

def email_template(vn,nn,info,extra):
    name = " ".join(["Sehr geehrte/r",vn,nn])
    gruss = "\n\nMit freundlichen Grüßen,\nPraxis Matthess (IT Abteilung)"
    return "".join([name,info,extra,gruss])

async def invite_patient(vn,nn,link,email):
    info = """\n\nWir freuen uns, Sie als Patient in unserer Praxis zu begrüßen. Bitte beantworten Sie das folgende Formular. Der Link ist 2 Wochen lang gültig und kann nur einmal genutzt werden. Nach Aktivierung des Links haben Sie 2 Stunden, um das kurze Formular auszufüllen. Bei Fragen und technischen Problemen können Sie uns gerne kontaktieren.\n\nMit diesem Link können Sie das Formular erreichen:\n\n""" 
    text = email_template(vn,nn,info,link) 
    await send_email(email,"Psychologische Ersteinschätzung",text)

async def answer_patient(vn,nn,result,email):
    info = """ 
        \n\nHerzlichen Dank für das Ausfüllen unseres Formulars zur psychologischen Ersteinschätzung. Der Test hat Sie auf häufige Persönlichkeitsstörungen sowie ADHS schnell-geprüft. Die Wahrscheinlichkeit eines falsch-positiven Ergebnisses ist dabei höher als die eines falsch-negativen Ergebnisses. Folgende Werte sind möglich: sehr unwahrscheinlich, möglich, wahrscheinlich, sehr wahrscheinlich. Ihr Test hat folgendes ergeben:\n\n
        """
    text = email_template(vn,nn,info,result) 
    await send_email(email,"Automatisches Ergebnis der psychologischen Ersteinschätzung",text)



# TESTS #


async def new_test(pid : str, result: str, c: syncpg.Connection) -> int:
    return await c.fetchval(
        """INSERT INTO test (patient_id, ergebnis) VALUES ($1, $2) RETURNING id;""", 
        pid,result
        )

async def new_answer(qid : str, answer, tid:int, c: syncpg.Connection):
    fragentyp = await c.fetchval(
        """SELECT typ FROM Frage where id = ($1);""",qid
        )
    query = f'INSERT INTO antwort (test_id, frage_id, {fragentyp}) VALUES ($1, $2, $3);'
    await c.execute(
        query,tid,qid,answer
        )


def compute_result(answers:dict) -> str:
    gen_res = 0
    adhs_res = 0
    for key, value in answers.items():
        if key.startswith("q1"):
            gen_res += scales["gen_vals"][value]
        elif key.startswith("q2"):
            adhs_res += scales["adhs_vals"][value]
    for k,v in scales["gen_scale"].items():
        if gen_res in k:
            gen = v
    for k,v in scales["adhs_scale"].items():
        if adhs_res in k:
            adhs = v
    return "".join(["Es ist ",gen,""", dass Sie unter einer Persönlichkeitsstörung leiden.\nEs ist """,adhs,", dass Sie unter ADHS leiden."])



app.mount("/pages", StaticFiles(directory="static"), name="static")



