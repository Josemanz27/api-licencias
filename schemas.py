from pydantic import BaseModel
from datetime import date

# Modelo de Pydantic para los datos de entrada

class Licencia(BaseModel):
    conductor_name: str
    tipo: str
    fecha_expedicion: date
    numero: str

class Vigencia(BaseModel)
    licencia_id: int
    fecha_ini_vig: date
    fecha_fin_vig: date

class Estado(BaseModel)
    vigencia_id: int
    estado: str
    fecha_estado: date

class LicenciaUpdate(BaseModel):
    conductor_name: str
    tipo: str
    fecha_expedicion: date

class VigenciaUpdate(BaseModel):
    fecha_ini_vig: date
    fecha_fin_vig: date

class EstadoUpdate(BaseModel):
    estado: str = Field(None)
    fecha_estado: date = Field(None)

class VigenciaResponse(BaseModel):
    id: int
    licencia_id: int
    fecha_ini_vig: date
    fecha_fin_vig: date
    class Config:
        orm_mode = True

class EstadoResponse(BaseModel):
    id: int
    vigencia_id: int
    estado: str
    fecha_estado: date
    class Config:
        orm_mode = True

class LicenciaConFechaExpiracion(BaseModel):
    id: int
    conductor_name: str
    tipo: str
    fecha_expedicion: date
    numero: str
    fecha_expiracion: date  # Campo nuevo
    class Config:
        orm_mode = True