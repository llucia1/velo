#!/usr/bin/env python3
"""Crea la base SQLite de productos de proveedores en shared.

Por defecto la base se crea en /shared/BDs/SQLite/proveedores/proveedores.db
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

# 1. Obtenemos la ruta base (por defecto /shared dentro del contenedor)
SHARED_DIR = Path(os.environ.get("SHARED_DIR", "/shared"))

# 2. Creamos la subcarpeta CORRECTAMENTE (sin os.environ.get repetido y sin la barra "/" antes de BDs)
SHARED_SQLITE_PROVEEDORES_DIR = SHARED_DIR / "BDs/SQLite/proveedores"

# 3. Ruta final del archivo .db
DB_PATH = Path(os.environ.get("SQLITE_DB_PATH", SHARED_SQLITE_PROVEEDORES_DIR / "proveedores_bd.db"))

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS proveedores (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre          TEXT NOT NULL,
    url             TEXT NOT NULL,
    categoria_url   TEXT,
    producto_url    TEXT
);


CREATE TABLE IF NOT EXISTS productos (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    proveedor_id             INTEGER  DEFAULT 1,
    referencia               TEXT DEFAULT NULL,
    titulo                   TEXT NOT NULL,
    ean                       TEXT DEFAULT NULL,
    precio_proveedor          REAL NOT NULL,
    descripcion                 TEXT,
    descripcion_ampliada         TEXT DEFAULT NULL,
    stock                     INTEGER DEFAULT 0,
    tiene_variantes           INTEGER DEFAULT 0,
    url_proveedor              TEXT NOT NULL,
    slug_categoria_origen      TEXT,
    id_producto_ps              INTEGER,
    sincronizado                INTEGER DEFAULT 0,
    fecha_scrapeo                TEXT NOT NULL,
    fecha_sincronizacion          TEXT,
    fecha_SEO          TEXT,
    titulo_SEO                   TEXT,
    descripcion_SEO                 TEXT,
    keywords_SEO                 TEXT,


    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
);


CREATE UNIQUE INDEX IF NOT EXISTS idx_proveedor_id ON productos(proveedor_id);
CREATE INDEX IF NOT EXISTS idx_referencia ON productos(referencia);


CREATE TABLE IF NOT EXISTS producto_imagenes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id     TEXT NOT NULL,
    url             TEXT NOT NULL,
    orden           INTEGER NOT NULL,      -- 0 = principal, 1, 2... = galería
    es_principal    INTEGER DEFAULT 0,

    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

CREATE INDEX IF NOT EXISTS idx_img_producto ON producto_imagenes(producto_id);


-- ==============================================================================
-- producto_variantes
-- Solo se rellena cuando productos.tiene_variantes = 1
-- ==============================================================================
CREATE TABLE IF NOT EXISTS producto_variantes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id      TEXT NOT NULL,
    referencia      TEXT,                  -- ej. "99324A"
    atributo_grupo  TEXT,                  -- ej. "MEDIDA"
    atributo_valor  TEXT,                  -- ej. "28.6"
    precio          REAL NOT NULL,

    FOREIGN KEY (producto_id) REFERENCES productos(id)
);

CREATE INDEX IF NOT EXISTS idx_var_producto ON producto_variantes(producto_id);
CREATE INDEX IF NOT EXISTS idx_var_referencia ON producto_variantes(referencia);



-- ==============================================================================
-- categorias
-- categorías de PS y asociadas al Proveedor
-- ==============================================================================
CREATE TABLE IF NOT EXISTS categorias (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    provedor_id      INTEGER NOT NULL,
    id_categoria_ps     INTEGER NOT NULL,   -- el ID que generamos en el scraper de categorías (100+)
    id_categoria_parent_ps     INTEGER,
    slug_categoria_provedor       TEXT NOT NULL,      -- para trazabilidad, ej. "/shop/category/componentes-horquillas-18-204"

    FOREIGN KEY (provedor_id) REFERENCES proveedores(id)
    FOREIGN KEY (id_categoria_parent_ps) REFERENCES categorias(id)
);

CREATE INDEX IF NOT EXISTS idx_categorias_producto ON categorias(id_categoria_ps);







-- ==============================================================================
-- producto_categorias
-- Relación N a N — resuelve el problema de productos en varias categorías
-- ==============================================================================
CREATE TABLE IF NOT EXISTS producto_categorias (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    producto_id      TEXT NOT NULL,
    id_categoria_ps     INTEGER NOT NULL,   -- el ID que generamos en el scraper de categorías (100+)
    slug_categoria       TEXT NOT NULL,      -- para trazabilidad, ej. "/shop/category/componentes-horquillas-18-204"

    FOREIGN KEY (producto_id) REFERENCES productos(id),
    UNIQUE (producto_id, id_categoria_ps)    -- evita duplicar la misma categoría para el mismo producto
);

CREATE INDEX IF NOT EXISTS idx_cat_producto ON producto_categorias(producto_id);
CREATE INDEX IF NOT EXISTS idx_cat_id_ps ON producto_categorias(id_categoria_ps);







"""

def init_db(db_path: Path = DB_PATH) -> Path:
    """Crea la base SQLite proveedores y devuelve la ruta usada."""
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as connection:
        connection.executescript(SCHEMA)
        connection.commit()

    return db_path


def main() -> None:
    db_path = init_db()
    print(f"Base SQLite proveedores lista: {db_path}")


if __name__ == "__main__":
    main()