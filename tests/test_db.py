import sqlite3
import os


def test_db_exists():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "data", "almacen.db")
    assert os.path.exists(
        db_path
    ), "La base de datos almacen.db no existe en la raíz del proyecto"
