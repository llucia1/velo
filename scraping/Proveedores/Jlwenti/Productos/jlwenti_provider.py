"""
Proveedores/Jlwenti/Productos/jlwenti_provider.py
==================================================
Implementación de ProductProvider para jlwenti.com (Odoo 16).
Responsable de:
  - Listar URLs de productos de una categoría (con paginación)
  - Parsear la página de un producto individual
"""

import re
import json
import time
import logging
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from Proveedores.contratos import ProductProvider
from Proveedores.Jlwenti.login import create_session, BASE_URL, HEADERS

log = logging.getLogger(__name__)

DELAY = 1.0  # segundos entre peticiones


class JlwentiProvider(ProductProvider):
    """Proveedor jlwenti.com — tienda Odoo 16."""

    base_url = BASE_URL
    delay    = DELAY

    def __init__(self, user: str = None, password: str = None):
        from Proveedores.Jlwenti.login import SUPPLIER_USER, SUPPLIER_PASS
        self._user     = user or SUPPLIER_USER
        self._password = password or SUPPLIER_PASS
        self._session  = None

    def login(self) -> bool:
        self._session = create_session(self._user, self._password)
        return self._session is not None

    # ------------------------------------------------------------------
    # LISTADO DE CATEGORÍA → URLs de producto
    # ------------------------------------------------------------------

    def get_product_urls_from_category(self, category_url: str) -> list[str]:
        """
        Devuelve todas las URLs de producto de una categoría,
        recorriendo la paginación si existe.
        Patrón Odoo: /shop/category/SLUG/page/N
        """
        seen = set()

        resp = self._session.get(category_url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, 'lxml')

        # Detectar total de páginas desde la paginación
        total_pages = 1
        pager = soup.find('ul', class_='pagination')
        if pager:
            page_numbers = [
                int(a.get_text(strip=True))
                for a in pager.find_all('a', class_='page-link')
                if a.get_text(strip=True).isdigit()
            ]
            if page_numbers:
                total_pages = max(page_numbers)

        log.info(f"    {total_pages} página(s)")

        urls = self._extract_urls_from_soup(soup, seen)

        for page_num in range(2, total_pages + 1):
            page_url = f"{category_url.rstrip('/')}/page/{page_num}"
            resp = self._session.get(page_url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            page_soup = BeautifulSoup(resp.text, 'lxml')
            urls += self._extract_urls_from_soup(page_soup, seen)
            time.sleep(self.delay)

        return urls

    def _extract_urls_from_soup(self, soup, seen: set) -> list[str]:
        """Extrae URLs de producto de una página de listado ya parseada."""
        urls = []
        for cell in soup.find_all('td', class_='oe_product'):
            link = cell.find('a', itemprop='url')
            if link and link.get('href'):
                href = link['href'].split('?')[0]  # quitar ?category=N
                full_url = urljoin(self.base_url, href)
                if full_url not in seen:
                    seen.add(full_url)
                    urls.append(full_url)
        return urls

    # ------------------------------------------------------------------
    # PARSEO DE PRODUCTO INDIVIDUAL
    # ------------------------------------------------------------------

    def parse_product(self, url: str) -> dict | None:
        """
        Visita la URL del producto y extrae todos sus datos.
        Devuelve None si no se puede parsear.
        """
        try:
            resp = self._session.get(url, headers=HEADERS, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'lxml')

            template_id = self._get_template_id(soup)
            if not template_id:
                log.warning(f"Sin template_id: {url}")
                return None

            tiene_variantes = not self._is_simple(soup)

            return {
                'template_id':       template_id,
                'referencia':        self._get_referencia(soup),
                'titulo':            self._get_titulo(soup),
                'ean':               self._get_ean(soup),
                'precio_proveedor':  self._get_precio(soup),
                'descripcion_corta': '',
                'descripcion_larga': self._get_descripcion_larga(soup),
                'stock':             self._get_stock(soup),
                'tiene_variantes':   tiene_variantes,
                'url_proveedor':     url,
                'imagenes':          self._get_imagenes(soup),
                'variantes':         self._get_variantes(soup) if tiene_variantes else [],
            }

        except Exception as e:
            log.error(f"Error parseando {url}: {e}")
            return None

    # ------------------------------------------------------------------
    # HELPERS DE EXTRACCIÓN
    # ------------------------------------------------------------------

    def _get_template_id(self, soup) -> str:
        el = soup.find('input', class_='product_template_id')
        return el['value'].strip() if el else ''

    def _get_titulo(self, soup) -> str:
        h1 = soup.find('h1', itemprop='name')
        if h1:
            return h1.get_text(strip=True)
        og = soup.find('meta', property='og:title')
        if og and og.get('content'):
            return og['content'].split('|')[0].strip()
        return ''

