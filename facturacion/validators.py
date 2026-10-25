"""
Validadores específicos para Ecuador (Cédula y RUC según algoritmo SRI).
"""
import re
from django.core.exceptions import ValidationError


def validar_cedula_ecuador(cedula: str) -> bool:
    """
    Valida número de cédula ecuatoriana (10 dígitos).
    Aplica algoritmo de módulo 10.
    """
    if not cedula or not re.match(r'^\d{10}$', cedula):
        return False

    provincia = int(cedula[0:2])
    if not (1 <= provincia <= 24 or provincia == 30):
        return False

    tercer_digito = int(cedula[2])
    if tercer_digito >= 6:
        return False

    coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
    suma = 0
    for i in range(9):
        val = int(cedula[i]) * coeficientes[i]
        if val >= 10:
            val -= 9
        suma += val

    digito_verificador = (10 - (suma % 10)) % 10
    return digito_verificador == int(cedula[9])


def validar_ruc_ecuador(ruc: str) -> bool:
    """
    Valida número de RUC ecuatoriano (13 dígitos).
    Soporta:
    1. Persona natural (cédula + 001)
    2. Sociedad privada / extranjera (3er dígito 9)
    3. Entidad pública (3er dígito 6)
    4. Consumidor final (9999999999999)
    """
    if not ruc or not re.match(r'^\d{13}$', ruc):
        return False

    if ruc == '9999999999999':
        return True

    provincia = int(ruc[0:2])
    if not (1 <= provincia <= 24 or provincia == 30):
        return False

    tercer_digito = int(ruc[2])

    # 1. Persona Natural: Cédula válida + establecimiento '001' (o >= '001')
    if tercer_digito < 6:
        if not validar_cedula_ecuador(ruc[:10]):
            return False
        establecimiento = int(ruc[10:])
        return establecimiento >= 1

    # 2. Institución Pública: 3er dígito 6, módulo 11
    elif tercer_digito == 6:
        if int(ruc[9:]) < 1:  # últimos 4 dígitos no pueden ser 0000
            return False
        coeficientes = [3, 2, 7, 6, 5, 4, 3, 2]
        suma = sum(int(ruc[i]) * coeficientes[i] for i in range(8))
        residuo = suma % 11
        digito_verificador = 0 if residuo == 0 else (11 - residuo)
        return digito_verificador == int(ruc[8])

    # 3. Sociedad Privada / Extranjeros: 3er dígito 9, módulo 11
    elif tercer_digito == 9:
        if int(ruc[10:]) < 1:  # últimos 3 dígitos no pueden ser 000
            return False
        coeficientes = [4, 3, 2, 7, 6, 5, 4, 3, 2]
        suma = sum(int(ruc[i]) * coeficientes[i] for i in range(9))
        residuo = suma % 11
        digito_verificador = 0 if residuo == 0 else (11 - residuo)
        return digito_verificador == int(ruc[9])

    return False


def validar_identificacion_ecuador(tipo: str, numero: str):
    """
    Validador para formularios y modelos de Django.
    """
    numero = (numero or '').strip()
    if tipo == '05':  # Cédula
        if not validar_cedula_ecuador(numero):
            raise ValidationError(f"La cédula '{numero}' no es válida según el estándar del Registro Civil de Ecuador.")
    elif tipo == '04':  # RUC
        if not validar_ruc_ecuador(numero):
            raise ValidationError(f"El RUC '{numero}' no es válido según el algoritmo del SRI.")
    elif tipo == '07':  # Consumidor Final
        if numero != '9999999999999':
            raise ValidationError("Para Consumidor Final, el número debe ser 9999999999999.")
    elif tipo == '06':  # Pasaporte
        if len(numero) < 3:
            raise ValidationError("El pasaporte debe tener al menos 3 caracteres.")
