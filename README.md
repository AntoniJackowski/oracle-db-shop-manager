# System Zarządzania Sklepem Spożywczym

Aplikacja desktopowa w języku Python z graficznym interfejsem użytkownika (GUI), zintegrowana z relacyjną bazą danych Oracle. Projekt umożliwia kompleksowe zarządzanie asortymentem sklepu, pracownikami, klientami oraz zamówieniami.

## Technologie
* **Baza Danych:** Oracle SQL, PL/SQL (procedury składowane, wyzwalacze)
* **Aplikacja (Backend & GUI):** Python 3, Tkinter, `oracledb`
* **Raportowanie:** `fpdf` (generowanie plików PDF), `matplotlib` (wykresy)

## Główne funkcje
* **Zarządzanie danymi (CRUD):** Przeglądanie, dodawanie i usuwanie produktów, klientów, dostawców i magazynów z poziomu aplikacji.
* **Zaawansowane mechanizmy Oracle:** Wykorzystanie procedur składowanych (np. system przyznawania premii) oraz wyzwalaczy (automatyczna walidacja cen i oznaczanie promocji).
* **Automatyczne raporty:** Generowanie cenników, kart klientów oraz statystyk magazynowych w formie dokumentów PDF z wykresami.

## Struktura projektu
* `main_gui.py` - Główny skrypt aplikacji (interfejs użytkownika).
* `db_operations.py` - Moduł do komunikacji z bazą danych Oracle.
* `report_manager.py` - Skrypt generujący raporty PDF i wykresy.
* `Sklep_DDL_DML_Full.sql` - Skrypt SQL tworzący tabele, relacje i wprowadzający przykładowe dane.
* `Dokumentacja.pdf` - Dokumentacja z diagramami ERD/UML i opisem logiki.

## Jak uruchomić?
1. Wykonaj skrypt `Sklep_DDL_DML_Full.sql` w swojej bazie Oracle.
2. Zainstaluj wymagane biblioteki:
   ```bash
   pip install oracledb fpdf matplotlib
