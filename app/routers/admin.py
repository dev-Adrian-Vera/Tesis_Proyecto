from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from db import modelos
from servicios.hist_inferencias import obtener_inferencias_admin
from servicios.sesiones import obtener_sesiones_admin, obtener_usuarios
from db.database import get_db
from servicios.seguridad import get_current_user, require_admin
from servicios.log_errores import obtener_logs_error

router = APIRouter(
    prefix="/v1/admin/logs",
    tags=["Administración"]
)

@router.get("/errores")
def listar_logs_error(
    limite: int = 0,
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    logs = obtener_logs_error(db, limite)

    return [
        {
            "id_log": log.id_log_sis,
            "mensaje_error": log.mensaje_error,
            "fuente": log.fuente,
            "fecha": log.fecha_general_log,
            "id_usuario": log.id_usuario
        }
        for log in logs
    ]

@router.get("/listar_usuarios")
def listar_usuarios(
    db: Session = Depends(get_db),
    usuario = Depends(get_current_user)
):

    # Solo admins
    if usuario.role_id != 0:
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado, solo administradores pueden acceder a esta información."
        )

    usuarios = obtener_usuarios(db)

    return [
        {
            "rol": "admin" if u.role_id == 0 else "usuario",
            "id_usuario": u.id_usuario,
            "Nombre completo": u.nombre_completo,
            "email": u.email,
            "fecha_creacion": u.fecha_creacion.strftime("%d-%m-%Y %H:%M:%S")
        }
        for u in usuarios
    ]


@router.get("/Listar_sesiones")
def listar_sesiones(
    db: Session = Depends(get_db),
    usuario = Depends(get_current_user)
):
     # Solo admins
    if usuario.role_id != 0:
        raise HTTPException(
            status_code=403,
            detail="Acceso denegado, solo administradores pueden acceder a esta información."
        )
    
    sesiones = obtener_sesiones_admin(db, usuario)

    return [
        {
            "usuario": {
                "id": s.usuario.id_usuario,
                "email": s.usuario.email,
                "rol": "admin" if s.usuario.role_id == 0 else "usuario",
            },
            "fecha_ingreso": s.fecha_ingreso,
            "ip_origen": s.ip_origen,
            "agente": s.agente,
            "estado": s.estado,
            "observacion": s.observacion
        }
        for s in sesiones
    ]

@router.get("/historial")
def listar_inferencias(
    db: Session = Depends(get_db),
    usuario = Depends(get_current_user)

):
    inferencias = obtener_inferencias_admin(db, usuario)

    return [
        {
            "log_id": i.log_id,
            "prediccion": i.prediccion_especie,
            "confianza": i.confianza,
            "top_5": i.top_5,
            "tiempo_ejecucion": i.tiempo_ejecucion,
            "fecha": i.fecha_ejecuta,
            "usuario": db.query(modelos.Usuario).filter(modelos.Usuario.id_usuario == i.id_usuario).first().nombre_completo if i.id_usuario else "Anónimo"
        }
        for i in inferencias
    ]
