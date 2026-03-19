#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
import db_operations
from report_manager import ReportManager


class SklepApp:
    def __init__(self, root):
        """Inicjalizacja głównego okna aplikacji oraz konfiguracja systemu zakładek nawigacyjnych."""
        self.root = root
        self.root.title("System Zarządzania Sklepem")
        self.root.geometry("1000x600")

        # Implementacja kontenera zakładek do separacji widoków poszczególnych tabel
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both')

        # Inicjalizacja menedżera raportów
        self.report_mgr = ReportManager()

        # Wykaz encji bazy danych podlegających obsłudze w interfejsie użytkownika
        tabele = ["KATEGORIE", "DOSTAWCY", "KLIENCI", "MAGAZYNY", "PRODUKTY"]

        for nazwa in tabele:
            frame = ttk.Frame(self.notebook)
            self.notebook.add(frame, text=nazwa)
            self.setup_table_tab(frame, nazwa)

        self.tab_reports = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_reports, text="RAPORTY")
        self.setup_reports_tab()

    def setup_table_tab(self, frame, table_name):
        """Konfiguracja panelu wyszukiwania, przycisków sterujących oraz komponentu prezentacji danych."""
        # --- Panel Wyszukiwania i Kryteriów ---
        search_frame = ttk.LabelFrame(frame, text="Wyszukiwanie (Kryteria)")
        search_frame.pack(side="top", fill="x", padx=10, pady=5)

        ttk.Label(search_frame, text="Kolumna:").pack(side="left", padx=5, pady=5)
        # Komponent wyboru kolumny do filtrowania danych
        combo_search_col = ttk.Combobox(search_frame, state="readonly", width=20)
        combo_search_col.pack(side="left", padx=5, pady=5)

        ttk.Label(search_frame, text="Fraza:").pack(side="left", padx=5, pady=5)
        ent_search_val = ttk.Entry(search_frame, width=30)
        ent_search_val.pack(side="left", padx=5, pady=5)

        # --- Panel Przycisków Operacyjnych ---
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(side="top", fill="x", padx=10, pady=5)

        # Inicjalizacja komponentu Treeview do wyświetlania rekordów z bazy
        tree = ttk.Treeview(frame, columns=[], show='headings')
        tree.pack(expand=True, fill='both', padx=10, pady=5)

        # Definicja procedury realizującej wyszukiwanie dynamiczne
        def do_search():
            col = combo_search_col.get()
            val = ent_search_val.get()
            self.load_data(tree, table_name, col, val)

        # Definicja procedury przywracającej pełny widok danych
        def do_reset():
            ent_search_val.delete(0, tk.END)
            self.load_data(tree, table_name)

        ttk.Button(search_frame, text="Szukaj", command=do_search).pack(side="left", padx=5)
        ttk.Button(search_frame, text="Resetuj", command=do_reset).pack(side="left", padx=5)

        # Implementacja przycisków wywołujących operacje CRUD i odświeżanie
        ttk.Button(btn_frame, text="Odśwież",
                   command=lambda: self.load_data(tree, table_name)).pack(side="left")

        # Warunkowy wybór okna formularza w zależności od typu tabeli
        if table_name == "PRODUKTY":
            ttk.Button(btn_frame, text="Dodaj nowy",
                       command=lambda: self.open_add_product_window(tree)).pack(side="left", padx=5)
        else:
            ttk.Button(btn_frame, text="Dodaj nowy",
                       command=lambda: self.open_add_generic_window(table_name, tree)).pack(side="left", padx=5)

        ttk.Button(btn_frame, text="Usuń zaznaczone",
                   command=lambda: self.delete_selected(tree, table_name)).pack(side="left")

        # Inicjalne pobranie danych oraz mapowanie nazw kolumn do systemu wyszukiwania
        self.load_data(tree, table_name)
        combo_search_col['values'] = tree["columns"]
        if tree["columns"]:
            combo_search_col.current(1)  # Domyślny wybór drugiej kolumny (zazwyczaj atrybut opisowy)

    def load_data(self, tree, table_name, search_col=None, search_val=None):
        """Komunikacja z modułem db_operations w celu aktualizacji zawartości widoku danych."""
        cols, data = db_operations.fetch_all(table_name, search_col, search_val)

        # Konfiguracja struktury kolumn na podstawie deskryptorów z bazy danych
        tree["columns"] = cols
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=100)

        # Usunięcie nieaktualnych wpisów z interfejsu
        for item in tree.get_children():
            tree.delete(item)

        # Proces zasilania komponentu graficznego nowymi rekordami
        for row in data:
            tree.insert("", "end", values=row)

    def open_add_product_window(self, tree):
        """Inicjalizacja dedykowanego formularza dla tabeli PRODUKTY z obsługą mapowania kluczy obcych."""
        top = Toplevel(self.root)
        top.title("Dodaj nowy produkt")

        # Kontener główny zapewniający separację elementów od krawędzi okna
        main_frame = ttk.Frame(top, padding="20 20 20 20")
        main_frame.pack(expand=True, fill="both")

        SZEROKOSC_POLA = 50

        # Pobranie danych referencyjnych dla list rozwijanych (mapowanie Nazwa -> ID)
        dostawcy_map = db_operations.get_lookup_data("DOSTAWCY", "ID_DOSTAWCY",
                                                     "NAZWA")
        magazyny_map = db_operations.get_magazyny_lookup()
        kategorie_map = db_operations.get_lookup_data("KATEGORIE",
                                                      "ID_KATEGORII", "NAZWA")

        # Definicja etykiet i pól tekstowych dla atrybutów podstawowych
        ttk.Label(main_frame, text="NAZWA PRODUKTU:").pack(pady=2, anchor="w")
        ent_nazwa = ttk.Entry(main_frame, width=SZEROKOSC_POLA)
        ent_nazwa.pack()

        ttk.Label(main_frame, text="CENA:").pack(pady=2, anchor="w")
        ent_cena = ttk.Entry(main_frame, width=SZEROKOSC_POLA)
        ent_cena.pack()

        ttk.Label(main_frame, text="JEDNOSTKA (szt/kg):").pack(pady=2, anchor="w")
        ent_jednostka = ttk.Entry(main_frame, width=SZEROKOSC_POLA)
        ent_jednostka.pack()

        # Konfiguracja komponentów Combobox zapewniających poprawność więzów integralności (klucze obce)
        ttk.Label(main_frame, text="DOSTAWCA:").pack(pady=2, anchor="w")
        combo_dostawca = ttk.Combobox(main_frame,
                                      values=list(dostawcy_map.keys()),
                                      state="readonly",
                                      width=SZEROKOSC_POLA - 3)
        combo_dostawca.pack()

        ttk.Label(main_frame, text="KATEGORIA:").pack(pady=2, anchor="w")
        combo_kategoria = ttk.Combobox(main_frame,
                                       values=list(kategorie_map.keys()),
                                       state="readonly",
                                       width=SZEROKOSC_POLA - 3)
        combo_kategoria.pack()

        ttk.Label(main_frame, text="MAGAZYN:").pack(pady=2, anchor="w")
        combo_magazyn = ttk.Combobox(main_frame,
                                     values=list(magazyny_map.keys()),
                                     state="readonly",
                                     width=SZEROKOSC_POLA - 3)
        combo_magazyn.pack()

        # Obsługa atrybutu wielowartościowego wprowadzanego jako ciąg znaków
        ttk.Label(main_frame, text="ALERGENY (rozdzielone przecinkiem):").pack(pady=2, anchor="w")
        ent_alergeny = ttk.Entry(main_frame, width=SZEROKOSC_POLA)
        ent_alergeny.pack()

        def save():
            """Proces gromadzenia danych, walidacji typów oraz wywołania procedury wstawiania do bazy."""
            try:
                # Transformacja danych z formularza na strukturę słownikową z uwzględnieniem mapowania ID
                data = {
                    'NAZWA': ent_nazwa.get(),
                    'CENA': float(ent_cena.get()),
                    'JEDNOSTKA_MIARY': ent_jednostka.get(),
                    'KOD_KRESKOWY': "",
                    'DOSTAWCA_ID': dostawcy_map[combo_dostawca.get()],
                    'MAGAZYN_ID': magazyny_map[combo_magazyn.get()],
                    'KATEGORIA_ID': kategorie_map[combo_kategoria.get()]
                }

                if db_operations.insert_product(data, ent_alergeny.get()):
                    messagebox.showinfo("Sukces",
                                        "Operacja zakończona powodzeniem.")
                    top.destroy()
                    self.load_data(tree, "PRODUKTY")
                else:
                    messagebox.showerror("Błąd",
                                         "Błąd podczas zapisu w bazie danych.")
            except Exception as e:
                messagebox.showerror("Błąd walidacji",
                                     f"Niepoprawne dane: {e}")

        ttk.Button(main_frame, text="Zapisz", command=save).pack(pady=20)

    def open_add_generic_window(self, table_name, tree):
        """Inicjalizacja dynamicznego okna formularza dla tabel o prostych strukturach atrybutów."""
        top = Toplevel(self.root)
        top.title(f"Dodaj: {table_name}")

        # Konfiguracja kontenera z marginesami wewnętrznymi
        main_frame = ttk.Frame(top, padding="20 20 20 20")
        main_frame.pack(expand=True, fill="both")

        # Mapowanie wymaganych pól wejściowych dla poszczególnych tabel
        fields_config = {
            "KATEGORIE": ["NAZWA"],
            "DOSTAWCY": ["NAZWA", "NIP", "NR_TEL", "ADRES"],
            "KLIENCI": ["IMIE", "NAZWISKO", "NR_TEL", "EMAIL",
                        "KARTA_RABATOWA"],
            "MAGAZYNY": ["SEGMENT", "OPIS"]
        }

        fields = fields_config.get(table_name, [])
        entries = {}

        # Automatyczne generowanie etykiet i pól tekstowych na podstawie konfiguracji
        for field in fields:
            ttk.Label(main_frame, text=f"{field}:").pack(pady=2, anchor="w")
            ent = ttk.Entry(main_frame, width=40)
            ent.pack(pady=5, fill="x")
            entries[field] = ent

        def save():
            """Gromadzenie danych z wygenerowanych pól i wywołanie uniwersalnej procedury zapisu."""
            data = {field: ent.get() for field, ent in entries.items()}
            if db_operations.insert_generic(table_name, data):
                messagebox.showinfo("Sukces", "Rekord dodany.")
                top.destroy()
                self.load_data(tree, table_name)

            else:
                messagebox.showerror("Błąd", "Nie udało się zapisać danych.")

        ttk.Button(main_frame, text="Zapisz", command=save).pack(pady=15)
    def delete_selected(self, tree, table_name):
        """Procedura weryfikacji zaznaczenia oraz wywołania operacji usuwania rekordu z bazy danych."""
        selected_item = tree.selection()

        # Walidacja wystąpienia zdarzenia zaznaczenia elementu w widoku
        if not selected_item:
            messagebox.showwarning("Brak wyboru",
                                   "Proszę najpierw zaznaczyć rekord do usunięcia.")
            return

        # Ekstrakcja danych z zaznaczonego wiersza w celu identyfikacji klucza głównego
        item_values = tree.item(selected_item)['values']
        id_val = item_values[0]
        id_col = tree["columns"][0]

        # Wymagane potwierdzenie przed nieodwracalną zmianą stanu bazy danych
        if messagebox.askyesno("Potwierdzenie",
                               f"Czy na pewno usunąć rekord o ID: {id_val}?"):
            try:
                # Wywołanie procedury usuwania z obsługą integralności w db_operations
                db_operations.delete_record(table_name, id_col, id_val)
                messagebox.showinfo("Sukces", "Rekord został usunięty.")
                # Aktualizacja interfejsu w celu odzwierciedlenia zmian w bazie
                self.load_data(tree, table_name)
            except Exception as e:
                messagebox.showerror("Błąd",
                                     f"Nie udało się usunąć rekordu: {e}")

    def setup_reports_tab(self):
        frame = ttk.Frame(self.tab_reports, padding="20")
        frame.pack(expand=True, fill="both")

        # Raport Produktów (Grupowanie + 2 kryteria)
        sect1 = ttk.LabelFrame(frame, text="Raport Produktów",
                               padding="10")
        sect1.pack(fill="x", pady=5)
        ttk.Label(sect1, text="Cena min:").grid(row=0, column=0)
        self.ent_min = ttk.Entry(sect1, width=10);
        self.ent_min.grid(row=0, column=1);
        self.ent_min.insert(0, "0")
        ttk.Label(sect1, text="Cena max:").grid(row=0, column=2)
        self.ent_max = ttk.Entry(sect1, width=10);
        self.ent_max.grid(row=0, column=3);
        self.ent_max.insert(0, "10")
        ttk.Button(sect1, text="Generuj",
                   command=lambda: self.report_mgr.raport_produkty_ceny(
                       self.ent_min.get(), self.ent_max.get())).grid(row=0,
                                                                     column=4,
                                                                     padx=10)

        # Statystyka (Wykres)
        sect2 = ttk.LabelFrame(frame, text="Statystyka Magazynu",
                               padding="10")
        sect2.pack(fill="x", pady=5)
        ttk.Button(sect2, text="Generuj Raport z Wykresem",
                   command=self.report_mgr.raport_statystyka_magazynu).pack()

        # Formularz Klienta
        sect3 = ttk.LabelFrame(frame, text="Karta Klienta",
                               padding="10")
        sect3.pack(fill="x", pady=5)
        ttk.Label(sect3, text="Nazwisko klienta:").grid(row=0, column=0)
        self.ent_klient = ttk.Entry(sect3);
        self.ent_klient.grid(row=0, column=1)
        ttk.Button(sect3, text="Generuj Kartę",
                   command=lambda: self.report_mgr.raport_karta_klienta(
                       self.ent_klient.get())).grid(row=0, column=2, padx=10)

        # Lista Dostawców
        sect4 = ttk.LabelFrame(frame, text="Lista Dostawców",
                               padding="10")
        sect4.pack(fill="x", pady=5)
        ttk.Button(sect4, text="Generuj Listę",
                   command=self.report_mgr.raport_lista_dostawcow).pack()


if __name__ == "__main__":
    # Start pętli głównej aplikacji
    root = tk.Tk()
    app = SklepApp(root)
    root.mainloop()
