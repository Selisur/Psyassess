from enum import Enum
from pydantic import BaseModel, Field, EmailStr, SecretStr
from datetime import datetime 
from uuid import UUID


class Patient(BaseModel):
    pid: UUID
    beigetreten: datetime
    vornamen: str = Field(max_length=60)
    nachnamen: str = Field(max_length=60)
    email: EmailStr 
    model_config = {"extra":"forbid"}

class Einladung(BaseModel):
    vornamen : str
    nachnamen : str
    email : EmailStr
    pw : SecretStr
    model_config = {"extra":"forbid"}


class Login(BaseModel):
    token : SecretStr
    model_config = {"extra":"forbid"}




class mc3(str, Enum):
    Nein = "Nein"
    Vielleicht = "Vielleicht"
    Ja = "Ja"

class mc5(str, Enum):
    Nie = "Nie"
    Selten = "Selten"
    Manchmal = "Manchmal"
    Oft  = "Oft"
    Sehr_oft = "Sehr oft"


class Selbsttest(BaseModel):
    q11: mc3
    q12: mc3
    q13: mc3
    q14: mc3
    q15: mc3
    q16: mc3
    q17: mc3
    q18: mc3
    q21: mc5
    q22: mc5
    q23: mc5
    q24: mc5
    q25: mc5
    q26: mc5
    q31: str = Field(max_length=2000)
    q32: str = Field(max_length=2000)
    q33: str = Field(max_length=2000)
    model_config = {"extra":"forbid"}


