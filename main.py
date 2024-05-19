from fastapi import FastAPI, HTTPException, Depends
import mysql.connector
from typing import List
import schemas  # Importar los esquemas desde schemas.py

app = FastAPI()

host_name = "52.6.145.141"
port_number = "8006"
user_name = "root"
password_db = "jjj"
database_name = "bd_api_licencias"

# Conectar a la base de datos
def get_db_connection():
    return mysql.connector.connect(
        host=host_name,
        port=port_number,
        user=user_name,
        password=password_db,
        database=database_name
    )

# Endpoint para crear una nueva licencia
@app.post("/licencias")
def create_licencia(licencia: schemas.Licencia, mydb=Depends(get_db_connection)):
    cursor = mydb.cursor()
    sql = "INSERT INTO licencia (conductor_name, tipo, fecha_expedicion, numero) VALUES (%s, %s, %s, %s)"
    val = (licencia.conductor_name, licencia.tipo, licencia.fecha_expedicion, licencia.numero)
    cursor.execute(sql, val)
    mydb.commit()
    mydb.close()
    return {"message": "Licencia creada con éxito"}

# Endpoint para agregar una nueva vigencia
@app.post("/vigencias/", status_code=201)
def agregar_vigencia(nueva_vigencia: Vigencia, mydb=Depends(get_db_connection)):
    cursor = mydb.cursor()
    sql = "INSERT INTO vigencia (licencia_id, fecha_ini_vig, fecha_fin_vig) VALUES (%s, %s, %s)"
    val = (nueva_vigencia.licencia_id, nueva_vigencia.fecha_ini_vig, nueva_vigencia.fecha_fin_vig)
    try:
        cursor.execute(sql,val)
        mydb.commit()
    except mysql.connector.Error as err:
        mydb.rollback()
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {err.msg}")
    finally:
        cursor.close()
        mydb.close()
    return {"message": "Vigencia añadida exitosamente"}
    
# Endpoint para agregar un nuevo estado
@app.post("/estados/", status_code=201)
def agregar_estado(nuevo_estado: Estado, mydb=Depends(get_db_connection)):
    cursor = mydb.cursor()
    sql = "INSERT INTO estado (vigencia_id, estado, fecha_estado) VALUES (%s, %s, %s)"
    val = (nuevo_estado.vigencia_id, nuevo_estado.estado, nuevo_estado.fecha_estado)
    try:
        cursor.execute(sql,val)
        mydb.commit()
    except mysql.connector.Error as err:
        mydb.rollback()
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {err.msg}")
    finally:
        cursor.close()
        mydb.close()
    return {"message": "Estado añadido exitosamente"}

# Endpoint para actualizar una licencia
@app.patch("/licencias/{licencia_id}")
def actualizar_licencia(licencia_id: int, licencia: LicenciaUpdate, db=Depends(get_db_connection)):
    updates = licencia.dict(exclude_unset=True)
    set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
    params = list(updates.values())
    params.append(licencia_id)

    if not updates:
        return {"message": "No se proporcionaron datos para actualizar."}

    cursor = db.cursor()
    try:
        cursor.execute(f"UPDATE licencia SET {set_clause} WHERE id = %s", params)
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Licencia no encontrada")
    finally:
        cursor.close()
        db.close()
    return {"message": "Licencia actualizada exitosamente"}

# Endpoint para actualizar una vigencia
@app.patch("/vigencias/{vigencia_id}")
def actualizar_vigencia(vigencia_id: int, vigencia: VigenciaUpdate, db=Depends(get_db_connection)):
    updates = vigencia.dict(exclude_unset=True)
    set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
    params = list(updates.values())
    params.append(vigencia_id)

    if not updates:
        return {"message": "No se proporcionaron datos para actualizar."}

    cursor = db.cursor()
    try:
        cursor.execute(f"UPDATE vigencia SET {set_clause} WHERE id = %s", params)
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Vigencia no encontrada")
    finally:
        cursor.close()
        db.close()
    return {"message": "Vigencia actualizada exitosamente"}

# Endpoint para actualizar un estado
@app.patch("/estados/{estado_id}")
def actualizar_estado(estado_id: int, estado: EstadoUpdate, db=Depends(get_db_connection)):
    updates = estado.dict(exclude_unset=True)
    set_clause = ", ".join([f"{key} = %s" for key in updates.keys()])
    params = list(updates.values())
    params.append(estado_id)

    if not updates:
        return {"message": "No se proporcionaron datos para actualizar."}

    cursor = db.cursor()
    try:
        cursor.execute(f"UPDATE estado SET {set_clause} WHERE id = %s", params)
        db.commit()
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Estado no encontrado")
    finally:
        cursor.close()
        db.close()
    return {"message": "Estado actualizado exitosamente"}

# Endpoint para consultar una licencia por ID
@app.get("/licencias/{numero}")
def get_licencia(numero: str, mydb=Depends(get_db_connection)):
    cursor = mydb.cursor(dictionary=True)
    sql = """select l.numero, l.conductor_name, l.tipo, l.fecha_expedicion, v.fecha_fin_vig as fecha_expiracion, e.estado, e.fecha_estado
                    from licencia l
                    left join vigencia v on l.id = v.licencia_id
                    left join estado e on v.id = e.vigencia_id
                    where l.numero = %s and e.id = (
                    select max(e.id)
                    from licencia ll
                    left join vigencia v on ll.id = v.licencia_id
                    left join estado e on v.id = e.vigencia_id
                    where ll.numero = %s)"""
    cursor.execute(sql,(numero,))
    result = cursor.fetchone()
    mydb.close()
    if result:
        return result
    else:
        raise HTTPException(status_code=404, detail="Licencia no encontrada")

# Endpoint para obtener todos las vigencias de una licencia
@app.get("/licencias/{licencia_id}/vigencias", response_model=List[VigenciaResponse])
def obtener_vigencias_licencia(licencia_id: int, db=Depends(get_db_connection)):
    cursor = db.cursor(dictionary=True)
    sql = "SELECT id, licencia_id, fecha_ini_vig, fecha_fin_vig FROM vigencia WHERE licencia_id = %s"
    try:
        cursor.execute(sql,(licencia_id,))
        vigencias = cursor.fetchall()
        if not vigencias:
            raise HTTPException(status_code=404, detail="No se encontraron vigencias para la licencia especificada")
    finally:
        cursor.close()
        db.close()
    return vigencias

# Endpoint para obtener todos los estados de una vigencia
@app.get("/vigencias/{vigencia_id}/estados", response_model=List[EstadoResponse])
def obtener_estados_vigencia(vigencia_id: int, db=Depends(get_db_connection)):
    cursor = db.cursor(dictionary=True)
    sql = "SELECT id, vigencia_id, estado, fecha_estado FROM estado WHERE vigencia_id = %s"
    try:
        cursor.execute(sql,(vigencia_id,))
        estados = cursor.fetchall()
        if not estados:
            raise HTTPException(status_code=404, detail="No se encontraron estados para la vigencia especificada")
    finally:
        cursor.close()
        db.close()
    return estados

# Endpoint para obtener todos las licencias de un conductor
@app.get("/licencias/conductor/{conductor_name}", response_model=List[LicenciaConFechaExpiracion])
def obtener_licencias_conductor(conductor_name: str, db=Depends(get_db_connection)):
    cursor = db.cursor(dictionary=True)
    sql = """
            SELECT l.id, l.conductor_name, l.tipo, l.fecha_expedicion, l.numero, MAX(v.fecha_fin_vig) AS fecha_expiracion
            FROM licencia l
            LEFT JOIN vigencia v ON l.id = v.licencia_id
            WHERE l.conductor_name = %s
            GROUP BY l.id
          """
    try:
        cursor.execute(sql,(conductor_name,))
        licencias = cursor.fetchall()
        if not licencias:
            raise HTTPException(status_code=404, detail="No se encontraron licencias para el conductor especificado")
    finally:
        cursor.close()
        db.close()
    return licencias

# Endpoint para eliminar una licencia
@app.delete("/licencias/{licencia_id}")
def eliminar_licencia(licencia_id: int, db=Depends(get_db_connection)):
    cursor = db.cursor()
    try:
        # Primero, verificar si la licencia existe
        cursor.execute("SELECT id FROM licencia WHERE id = %s", (licencia_id,))
        licencia = cursor.fetchone()
        if not licencia:
            raise HTTPException(status_code=404, detail="Licencia no encontrada")

        # Eliminar la licencia
        cursor.execute("DELETE FROM licencia WHERE id = %s", (licencia_id,))
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error de base de datos: {err.msg}")
    finally:
        cursor.close()
        db.close()
    return {"message": "Licencia eliminada exitosamente junto con todas sus vigencias y estados asociados"}