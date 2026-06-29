"""
Proveedores/contratos.py
========================
Contratos (interfaces) que debe cumplir cualquier proveedor.
"""

from abc import ABC, abstractmethod


class ProductProvider(ABC):
    """
    Contrato de proveedor de productos.
    Cualquier proveedor (Jlwenti, otro futuro) debe implementar esta clase.
    """

    base_url: str = ""
    delay: float = 1.0

    @abstractmethod
    def get_product_urls_from_category(self, category_url: str) -> list[str]:
        """
        Dada la URL de una categoría del proveedor,
        devuelve lista de URLs absolutas de sus productos (con paginación).
        """
        pass

    @abstractmethod
    def parse_product(self, url: str) -> dict | None:
        """
        Dada la URL de un producto, devuelve un dict con:
            template_id, referencia, titulo, ean, precio_proveedor,
            descripcion_corta, descripcion_larga, stock, tiene_variantes,
            url_proveedor, variantes[], imagenes[]
        Devuelve None si no se puede parsear.
        """
        pass


class CategoryFilter(ABC):
    """
    Contrato de filtro de categorías.
    Decide qué slugs de categoría procesar en cada ejecución.
    """

    @abstractmethod
    def get_slugs(self) -> list[str]:
        """Devuelve la lista de slugs a procesar."""
        pass
