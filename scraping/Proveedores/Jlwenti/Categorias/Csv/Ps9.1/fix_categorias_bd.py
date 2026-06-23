"""
fix_categorias_bd.py
====================
Ejecutar DESPUÉS de importar el CSV de categorías en PrestaShop.

El importador de PS ignora el id_parent del CSV para las categorías raíz
y siempre les asigna id_parent=1 (Raíz técnica) en lugar de id_parent=2 (Inicio).
Este script lo corrige directamente en MySQL.

Uso:
    pip install pymysql
    python fix_categorias_bd.py

Variables de entorno (ya definidas en docker-compose):
    MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
"""

import os
import logging
import pymysql

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

MYSQL_HOST     = os.environ.get("MYSQL_HOST", "mysql")
MYSQL_USER     = os.environ.get("MYSQL_USER", "prestashop")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "prestashop")
MYSQL_DB       = os.environ.get("MYSQL_DB", "prestashop")
DB_PREFIX      = os.environ.get("DB_PREFIX", "ps91_")
ID_START       = 100  # Nuestros IDs empiezan en 100

def main():
    log.info(f"Conectando a MySQL {MYSQL_HOST}/{MYSQL_DB}...")
    conn = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database=MYSQL_DB,
        charset='utf8mb4',
    )

    try:
        with conn.cursor() as cursor:
            # Verificar cuántas categorías raíz tienen id_parent=1
            cursor.execute(
                f"SELECT COUNT(*) FROM {DB_PREFIX}category "
                f"WHERE id_parent = 1 AND id_category >= %s",
                (ID_START,)
            )
            count = cursor.fetchone()[0]
            log.info(f"Categorías raíz con id_parent=1: {count}")

            if count == 0:
                log.info("Nada que corregir.")
                return

            # Corregir: id_parent=1 -> id_parent=2 (Inicio)
            cursor.execute(
                f"UPDATE {DB_PREFIX}category "
                f"SET id_parent = 2 "
                f"WHERE id_parent = 1 AND id_category >= %s",
                (ID_START,)
            )
            conn.commit()
            log.info(f"Corregidas {cursor.rowcount} categorías raíz -> id_parent=2 (Inicio)")

    finally:
        conn.close()

    log.info("=== DONE. Limpia la caché de PrestaShop para que los cambios sean visibles. ===")


if __name__ == '__main__':
    main()