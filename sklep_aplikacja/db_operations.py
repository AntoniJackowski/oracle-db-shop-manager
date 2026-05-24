#!/usr/bin/env python3

import oracledb

# Parametry konfiguracyjne niezbędne do nawiązania sesji z serwerem bazy danych Oracle
DB_CONFIG = {
    "user": "sklep_projekt",
    "password": "",
    "dsn": "localhost:1521/XEPDB1"
}


def get_connection():
    """Inicjalizuje i zwraca obiekt połączenia z bazą danych przy użyciu sterownika oracledb."""
    return oracledb.connect(**DB_CONFIG)


def fetch_all(table_name, search_col=None, search_val=None):
    """
    Realizuje pobieranie rekordów z bazy danych. W przypadku tabeli PRODUKTY
    implementuje zaawansowane złączenia (JOIN) oraz agregację danych wielowartościowych (LISTAGG).
    Obsługuje dynamiczne filtrowanie wyników na podstawie przekazanych parametrów.
    """
    conn = get_connection()
    cursor = conn.cursor()
    params = []

    # Implementacja logiki zapytania dla tabeli PRODUKTY z uwzględnieniem kluczy obcych i alergenów
    if table_name.upper() == "PRODUKTY":
        sql = """
            SELECT p.ID_PRODUKTU, p.NAZWA, p.CENA, p.JEDNOSTKA_MIARY, p.KOD_KRESKOWY,
                d.NAZWA as DOSTAWCA, m.SEGMENT as MAGAZYN, k.NAZWA as KATEGORIA,
                (SELECT LISTAGG(NAZWA_ALERGENU, ', ') WITHIN GROUP (ORDER BY NAZWA_ALERGENU)
                FROM PRODUKTY_ALERGENY pa WHERE pa.ID_PRODUKTU = p.ID_PRODUKTU) as ALERGENY
            FROM PRODUKTY p
            JOIN DOSTAWCY d ON p.DOSTAWCY_ID_DOSTAWCY = d.ID_DOSTAWCY
            JOIN MAGAZYNY m ON p.MAGAZYNY_ID_MAGAZYNU = m.ID_MAGAZYNU
            JOIN KATEGORIE k ON p.KATEGORIE_ID_KATEGORII = k.ID_KATEGORII
        """
        if search_col and search_val:
            # Rozszerzenie zapytania o klauzulę WHERE dla celów filtrowania frazowego
            sql += f" WHERE p.{search_col} LIKE :1"
            params.append(f"%{search_val}%")
    else:
        # Standardowe zapytanie typu SELECT dla pozostałych encji bazy danych
        sql = f"SELECT * FROM {table_name}"
        if search_col and search_val:
            sql += f" WHERE {search_col} LIKE :1"
            params.append(f"%{search_val}%")

    cursor.execute(sql, params)
    data = cursor.fetchall()
    # Wydobycie nazw kolumn
    cols = [col[0] for col in cursor.description]
    cursor.close()
    conn.close()
    return cols, data


def get_lookup_data(table, id_col, name_col):
    """Pobiera pary danych identyfikator-nazwa wykorzystywane do Combobox."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"SELECT {id_col}, {name_col} FROM {table}")
    # Mapowanie wyników do słownika
    lookup = {row[1]: row[0] for row in cursor}
    cursor.close()
    conn.close()
    return lookup


def get_magazyny_lookup():
    """
    Pobiera dane z tabeli MAGAZYNY i formatuje je w sposób czytelny dla operatora,
    łącząc nazwę segmentu z opcjonalnym opisem lokalizacji.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ID_MAGAZYNU, SEGMENT, OPIS FROM MAGAZYNY")

    lookup = {}
    for row in cursor:
        id_mag, segment, opis = row
        # Warunkowe formatowanie ciągu znaków wyświetlanego w interfejsie użytkownika
        tekst_wyswietlany = f"{segment} ({opis})" if opis else segment
        lookup[tekst_wyswietlany] = id_mag

    cursor.close()
    conn.close()
    return lookup


def insert_product(data, alergens_str):
    """
    Realizuje operację wstawiania produktu oraz powiązanych z nim alergenów.
    Zapewnia integralność operacji poprzez wykorzystanie mechanizmu transakcji (commit/rollback).
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Wstawienie danych do tabeli PRODUKTY z wykorzystaniem klauzuli RETURNING dla klucza głównego
        sql_prod = """
                   INSERT INTO PRODUKTY (NAZWA, CENA, JEDNOSTKA_MIARY, 
                                         KOD_KRESKOWY,
                                         DOSTAWCY_ID_DOSTAWCY, 
                                         MAGAZYNY_ID_MAGAZYNU, 
                                         KATEGORIE_ID_KATEGORII)
                   VALUES (:1, :2, :3, :4, :5, :6, :7) 
                   RETURNING ID_PRODUKTU INTO :8
                   """
        new_id_var = cursor.var(int)

        # Obsługa opcjonalności atrybutu KOD_KRESKOWY
        kod = data['KOD_KRESKOWY'] if data['KOD_KRESKOWY'].strip() else None

        cursor.execute(sql_prod, [
            data['NAZWA'], data['CENA'], data['JEDNOSTKA_MIARY'], kod,
            data['DOSTAWCA_ID'], data['MAGAZYN_ID'], data['KATEGORIA_ID'],
            new_id_var
        ])
        new_id = new_id_var.getvalue()[0]

        # Iteracyjne wstawianie rekordów do tabeli asocjacyjnej PRODUKTY_ALERGENY
        if alergens_str.strip():
            alergeny = [a.strip() for a in alergens_str.split(",")]
            for alergen in alergeny:
                cursor.execute(
                    "INSERT INTO PRODUKTY_ALERGENY (NAZWA_ALERGENU, ID_PRODUKTU) VALUES (:1, :2)",
                    [alergen, new_id]
                )

        conn.commit()
        return True
    except Exception as e:
        # Wycofanie wszystkich zmian w przypadku wystąpienia błędu podczas zapisu
        conn.rollback()
        print(f"Błąd operacji INSERT: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def insert_generic(table_name, data_dict):
    """
    Uniwersalny mechanizm wstawiania rekordów dla tabel o prostej strukturze danych.
    Dynamicznie buduje polecenie INSERT na podstawie struktury przekazanego słownika.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Konwersja pustych ciągów tekstowych na wartości NULL w celu zachowania spójności danych
    for key in data_dict:
        if isinstance(data_dict[key], str) and not data_dict[key].strip():
            data_dict[key] = None

    cols = ", ".join(data_dict.keys())
    placeholders = ", ".join([f":{i + 1}" for i in range(len(data_dict))])
    values = list(data_dict.values())

    sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"

    try:
        cursor.execute(sql, values)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Błąd INSERT w tabeli {table_name}: {e}")
        return False
    finally:
        cursor.close()
        conn.close()


def delete_record(table_name, id_col, id_val):
    """
    Usuwa wskazany rekord z bazy danych. Implementuje ręczne usuwanie kaskadowe
    dla powiązanych rekordów w tabeli alergenów przed usunięciem produktu nadrzędnego.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if table_name.upper() == "PRODUKTY":
            # Usunięcie zależności wynikających z więzów integralności (klucz obcy)
            cursor.execute(
                "DELETE FROM PRODUKTY_ALERGENY WHERE ID_PRODUKTU = :1",
                [id_val])

        cursor.execute(f"DELETE FROM {table_name} WHERE {id_col} = :1",
                       [id_val])
        conn.commit()
    finally:
        cursor.close()
        conn.close()
