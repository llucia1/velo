"""
Proveedores/Jlwenti/Categorias/Filter/category_filters.py
==========================================================
Implementaciones de CategoryFilter para jlwenti.com.
"""

from Proveedores.contratos import CategoryFilter
from Proveedores.Jlwenti.Categorias.jlwenti_slugs import ALL_SLUGS


class AllCategoriesFilter(CategoryFilter):
    """Procesa todas las categorías del proveedor (416)."""

    def get_slugs(self) -> list[str]:
        return ALL_SLUGS


class GroupCategoryFilter(CategoryFilter):
    """
    Procesa un grupo concreto de categorías.

    Uso:
        filter = GroupCategoryFilter([
            "/shop/category/componentes-sillines-67",
            "/shop/category/componentes-sillines-elastomeros-264",
        ])
    """

    def __init__(self, slugs: list[str]):
        self._slugs = slugs

    def get_slugs(self) -> list[str]:
        return self._slugs


class SingleCategoryFilter(CategoryFilter):
    """
    Procesa una sola categoría.

    Uso:
        filter = SingleCategoryFilter("/shop/category/componentes-sillines-elastomeros-264")
    """

    def __init__(self, slug: str):
        self._slug = slug

    def get_slugs(self) -> list[str]:
        return [self._slug]
