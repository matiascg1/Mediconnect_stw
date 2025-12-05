"""
Utilidades de formateo para MediConnect.
"""

import re
from datetime import datetime

def format_rut(rut: str) -> str:
    """
    Formatea un RUT chileno.
    - Elimina puntos
    - Lo deja en formato 12345678-9 (si ya viene así, lo devuelve igual)
    """
    if not rut:
        return ""
    
    rut = rut.replace(".", "").upper().strip()
    # Si no tiene guión, no intentamos inventarlo, solo lo devolvemos limpio
    return rut

def format_phone(phone: str) -> str:
    """
    Formatea un teléfono:
    - Deja solo dígitos
    - Opcionalmente podrías agregar +56, etc., pero por ahora lo mantenemos simple
    """
    if not phone:
        return ""
    
    digits = re.sub(r"\D", "", phone)
    return digits

def format_datetime(dt: datetime) -> str:
    """
    Formatea un datetime a string ISO 8601.
    """
    if not dt:
        return ""
    
    if isinstance(dt, datetime):
        return dt.isoformat()
    
    return str(dt)
