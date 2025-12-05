"""
Módulo de validaciones para MediConnect.
"""
import re
from typing import Optional, Dict, Any
from datetime import datetime

def validate_rut(rut: str) -> bool:
    """
    Valida un RUT chileno.
    
    Args:
        rut: RUT en formato 12345678-9
    
    Returns:
        True si el RUT es válido
    """
    if not rut:
        return False
    
    # Patrón básico
    pattern = r'^(\d{7,8})-([\dkK])$'
    match = re.match(pattern, rut)
    
    if not match:
        return False
    
    # Extraer número y dígito verificador
    numero = match.group(1)
    dv = match.group(2).upper()
    
    # Validar dígito verificador
    return _validate_rut_dv(numero, dv)

def _validate_rut_dv(numero: str, dv: str) -> bool:
    """Valida el dígito verificador de un RUT."""
    try:
        # Calcular dígito verificador esperado
        suma = 0
        multiplo = 2
        
        for digito in reversed(numero):
            suma += int(digito) * multiplo
            multiplo += 1
            if multiplo == 8:
                multiplo = 2
        
        resto = suma % 11
        dv_esperado = str(11 - resto) if resto != 0 else '0'
        
        # Casos especiales
        if dv_esperado == '10':
            dv_esperado = 'K'
        elif dv_esperado == '11':
            dv_esperado = '0'
        
        return dv == dv_esperado
        
    except:
        return False

def validate_email(email: str) -> bool:
    """
    Valida un email.
    
    Args:
        email: Email a validar
    
    Returns:
        True si el email es válido
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """
    Valida un número de teléfono chileno.
    
    Args:
        phone: Teléfono a validar
    
    Returns:
        True si el teléfono es válido
    """
    if not phone:
        return False
    
    # Limpiar espacios, guiones, paréntesis
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Patrones válidos
    patterns = [
        r'^\+569\d{8}$',      # +56912345678
        r'^569\d{8}$',        # 56912345678
        r'^9\d{8}$',          # 912345678
        r'^2\d{7,8}$',        # 21234567 o 212345678 (fijo)
        r'^32\d{6,7}$',       # 32123456 o 321234567 (fijo regional)
        r'^33\d{6,7}$',       # 33123456 o 331234567 (fijo regional)
        r'^34\d{6,7}$',       # 34123456 o 341234567 (fijo regional)
        r'^35\d{6,7}$',       # 35123456 o 351234567 (fijo regional)
        r'^41\d{6,7}$',       # 41123456 o 411234567 (fijo regional)
        r'^42\d{6,7}$',       # 42123456 o 421234567 (fijo regional)
        r'^43\d{6,7}$',       # 43123456 o 431234567 (fijo regional)
        r'^44\d{6,7}$',       # 44123456 o 441234567 (fijo regional)
        r'^45\d{6,7}$',       # 45123456 o 451234567 (fijo regional)
        r'^51\d{6,7}$',       # 51123456 o 511234567 (fijo regional)
        r'^52\d{6,7}$',       # 52123456 o 521234567 (fijo regional)
        r'^53\d{6,7}$',       # 53123456 o 531234567 (fijo regional)
        r'^55\d{6,7}$',       # 55123456 o 551234567 (fijo regional)
        r'^57\d{6,7}$',       # 57123456 o 571234567 (fijo regional)
        r'^58\d{6,7}$',       # 58123456 o 581234567 (fijo regional)
        r'^61\d{6,7}$',       # 61123456 o 611234567 (fijo regional)
        r'^63\d{6,7}$',       # 63123456 o 631234567 (fijo regional)
        r'^64\d{6,7}$',       # 64123456 o 641234567 (fijo regional)
        r'^65\d{6,7}$',       # 65123456 o 651234567 (fijo regional)
        r'^67\d{6,7}$',       # 67123456 o 671234567 (fijo regional)
        r'^71\d{6,7}$',       # 71123456 o 711234567 (fijo regional)
        r'^72\d{6,7}$',       # 72123456 o 721234567 (fijo regional)
        r'^73\d{6,7}$',       # 73123456 o 731234567 (fijo regional)
    ]
    
    return any(re.match(pattern, clean_phone) for pattern in patterns)

def validate_password(password: str) -> Optional[str]:
    """
    Valida la fortaleza de una contraseña.
    
    Args:
        password: Contraseña a validar
    
    Returns:
        None si es válida, mensaje de error si no
    """
    if not password:
        return "La contraseña no puede estar vacía"
    
    if len(password) < 8:
        return "La contraseña debe tener al menos 8 caracteres"
    
    if len(password) > 128:
        return "La contraseña no puede tener más de 128 caracteres"
    
    if not any(c.isupper() for c in password):
        return "La contraseña debe contener al menos una letra mayúscula"
    
    if not any(c.islower() for c in password):
        return "La contraseña debe contener al menos una letra minúscula"
    
    if not any(c.isdigit() for c in password):
        return "La contraseña debe contener al menos un número"
    
    # Opcional: caracteres especiales
    special_chars = r'[!@#$%^&*(),.?":{}|<>]'
    if not re.search(special_chars, password):
        return "La contraseña debe contener al menos un carácter especial (!@#$%^&*(), etc.)"
    
    return None

def validate_datetime(dt_str: str, future_only: bool = False) -> Optional[str]:
    """
    Valida una fecha y hora.
    
    Args:
        dt_str: String de fecha/hora en ISO format
        future_only: Si True, solo permite fechas futuras
    
    Returns:
        None si es válida, mensaje de error si no
    """
    if not dt_str:
        return "Fecha y hora requeridas"
    
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
    except (ValueError, TypeError):
        return "Formato de fecha inválido. Use ISO 8601 (YYYY-MM-DDTHH:MM:SS)"
    
    if future_only and dt < datetime.now():
        return "La fecha debe ser futura"
    
    return None

def validate_json_structure(data: Dict[str, Any], required_fields: Dict[str, type]) -> Optional[str]:
    """
    Valida la estructura de un JSON.
    
    Args:
        data: Datos a validar
        required_fields: Diccionario con campos requeridos y sus tipos
    
    Returns:
        None si es válido, mensaje de error si no
    """
    for field, field_type in required_fields.items():
        if field not in data:
            return f"Campo requerido faltante: {field}"
        
        value = data[field]
        
        # Validar tipo
        if field_type == str and not isinstance(value, str):
            return f"Campo {field} debe ser string"
        elif field_type == int and not isinstance(value, int):
            return f"Campo {field} debe ser entero"
        elif field_type == float and not isinstance(value, (int, float)):
            return f"Campo {field} debe ser número"
        elif field_type == bool and not isinstance(value, bool):
            return f"Campo {field} debe ser booleano"
        elif field_type == list and not isinstance(value, list):
            return f"Campo {field} debe ser lista"
        elif field_type == dict and not isinstance(value, dict):
            return f"Campo {field} debe ser diccionario"
        
        # Validaciones adicionales para strings
        if field_type == str and isinstance(value, str):
            if not value.strip():
                return f"Campo {field} no puede estar vacío"
    
    return None

def validate_appointment_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida datos de una cita médica.
    
    Args:
        data: Datos de la cita
    
    Returns:
        Dict con resultado de validación
    """
    # Campos requeridos
    required_fields = {
        'pacienteId': int,
        'medicoId': int,
        'fechaHora': str
    }
    
    error = validate_json_structure(data, required_fields)
    if error:
        return {'valid': False, 'message': error}
    
    # Validar fecha
    date_error = validate_datetime(data['fechaHora'], future_only=True)
    if date_error:
        return {'valid': False, 'message': date_error}
    
    return {'valid': True, 'message': 'Datos válidos'}

def validate_user_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida datos de un usuario.
    
    Args:
        data: Datos del usuario
    
    Returns:
        Dict con resultado de validación
    """
    # Campos requeridos para registro
    required_fields = {
        'nombre': str,
        'rut': str,
        'correo': str,
        'password': str
    }
    
    error = validate_json_structure(data, required_fields)
    if error:
        return {'valid': False, 'message': error}
    
    # Validar email
    if not validate_email(data['correo']):
        return {'valid': False, 'message': 'Email inválido'}
    
    # Validar RUT
    if not validate_rut(data['rut']):
        return {'valid': False, 'message': 'RUT inválido. Formato: 12345678-9'}
    
    # Validar contraseña
    password_error = validate_password(data['password'])
    if password_error:
        return {'valid': False, 'message': password_error}
    
    # Validar teléfono si se proporciona
    if 'telefono' in data and data['telefono']:
        if not validate_phone(data['telefono']):
            return {'valid': False, 'message': 'Teléfono inválido'}
    
    return {'valid': True, 'message': 'Datos válidos'}

def validate_prescription_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Valida datos de una receta médica.
    
    Args:
        data: Datos de la receta
    
    Returns:
        Dict con resultado de validación
    """
    required_fields = {
        'consultaId': int,
        'pacienteId': int,
        'medicoId': int,
        'medicamentos': list
    }
    
    error = validate_json_structure(data, required_fields)
    if error:
        return {'valid': False, 'message': error}
    
    # Validar medicamentos
    medicamentos = data.get('medicamentos', [])
    if not medicamentos:
        return {'valid': False, 'message': 'Debe incluir al menos un medicamento'}
    
    for i, med in enumerate(medicamentos):
        if not isinstance(med, dict):
            return {'valid': False, 'message': f'Medicamento {i+1} debe ser objeto'}
        
        if 'nombre' not in med or not med['nombre'].strip():
            return {'valid': False, 'message': f'Medicamento {i+1} debe tener nombre'}
        
        if 'dosis' not in med or not med['dosis'].strip():
            return {'valid': False, 'message': f'Medicamento {i+1} debe tener dosis'}
        
        if 'duracion' not in med or not med['duracion'].strip():
            return {'valid': False, 'message': f'Medicamento {i+1} debe tener duración'}
    
    return {'valid': True, 'message': 'Datos válidos'}
