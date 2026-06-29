"""
Proveedores/Jlwenti/login.py
=============================
Login en jlwenti.com (Odoo).
Reutilizable por cualquier clase del proveedor Jlwenti que necesite sesión autenticada.
"""

import os
import logging
import requests
from bs4 import BeautifulSoup

log = logging.getLogger(__name__)

BASE_URL      = "https://jlwenti.com"
LOGIN_URL     = f"{BASE_URL}/web/login"
SUPPLIER_USER = os.environ.get("SUPPLIER_USER", "bicis@bicicletadas.com")
SUPPLIER_PASS = os.environ.get("SUPPLIER_PASS", "Llucia-2018")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
}


def create_session(user: str = SUPPLIER_USER, password: str = SUPPLIER_PASS) -> requests.Session | None:
    """
    Crea una sesión HTTP autenticada en jlwenti.com.
    Devuelve la sesión si el login es correcto, None si falla.
    """
    session = requests.Session()
    session.headers.update(HEADERS)

    log.info(f"Login en {LOGIN_URL} como {user}...")

    try:
        r = session.get(LOGIN_URL, timeout=30)
        r.raise_for_status()
    except Exception as e:
        log.error(f"Error accediendo al login: {e}")
        return None

    soup = BeautifulSoup(r.text, 'lxml')
    csrf = soup.find('input', {'name': 'csrf_token'})
    if not csrf:
        log.error("csrf_token no encontrado en el formulario de login")
        return None

    try:
        r = session.post(LOGIN_URL, data={
            'login':      user,
            'password':   password,
            'csrf_token': csrf['value'],
            'redirect':   '/shop',
        }, headers={**HEADERS, 'Referer': LOGIN_URL}, timeout=30, allow_redirects=True)
        r.raise_for_status()
    except Exception as e:
        log.error(f"Error en POST login: {e}")
        return None

    if '/web/login' in r.url:
        log.error("Login fallido — credenciales incorrectas o sesión expirada")
        return None

    log.info("Login OK")
    return session
