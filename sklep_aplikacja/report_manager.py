import os
from fpdf import FPDF
import matplotlib.pyplot as plt
import db_operations
from matplotlib.ticker import MaxNLocator


class ReportManager:
    """Klasa odpowiedzialna za generowanie wszystkich raportów."""

    def __init__(self, output_dir="output"):
        """Inicjalizacja ścieżek czcionek oraz folderu wyjściowego dla gotowych dokumentów."""
        self.output_dir = output_dir
        # Wykorzystanie czcionek systemowych TrueType (TTF) w celu poprawnego renderowania polskich znaków
        self.font_path = r"C:\Windows\Fonts\arial.ttf"
        self.font_bold_path = r"C:\Windows\Fonts\arialbd.ttf"

        # Automatyczne tworzenie folderu wyjściowego, jeśli nie istnieje w katalogu projektu
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def _setup_pdf(self):
        """Pomocnicza metoda konfigurująca obiekt FPDF, rejestrująca czcionkę Unicode wspierającą polskie."""
        pdf = FPDF()
        # Dodanie zewnętrznych czcionek TTF do rejestru biblioteki fpdf2 (PolishArial)
        pdf.add_font("PolishArial", style="", fname=self.font_path)
        pdf.add_font("PolishArial", style="B", fname=self.font_bold_path)
        pdf.add_page()
        return pdf

    def _save_and_open(self, pdf, filename):
        """Finalizacja zapisu pliku PDF i automatyczne wywołanie systemowej przeglądarki dokumentów."""
        path = os.path.join(self.output_dir, filename)
        pdf.output(path)
        os.startfile(path)

    def raport_produkty_ceny(self, min_c, max_c):
        """Generuje raport produktów z podziałem na kategorie (grupowanie) w zadanym zakresie cenowym."""
        try:
            # Pobranie danych przy użyciu zdefiniowanych złączeń (JOIN) z modułu db_operations
            cols, data = db_operations.fetch_all("PRODUKTY")

            # Filtrowanie danych na podstawie 2 kryteriów (Cena Min/Max)
            filtered = [r for r in data if
                        float(min_c) <= float(r[2]) <= float(max_c)]

            # Przygotowanie danych do grupowania poprzez sortowanie po nazwie kategorii (indeks 7)
            filtered.sort(key=lambda x: x[7])

            pdf = self._setup_pdf()
            pdf.set_font("PolishArial", "B", 16)
            pdf.cell(0, 10, f"Produkty w zakresie {min_c} - {max_c} PLN",
                     ln=True, align='C')

            current_cat = None
            for row in filtered:
                # Logika wykrywania zmiany kategorii i wstawiania nagłówka grupy
                if row[7] != current_cat:
                    pdf.ln(5)
                    pdf.set_font("PolishArial", "B", 12)
                    pdf.set_fill_color(240, 240, 240)
                    pdf.cell(0, 10, f"KATEGORIA: {row[7]}", ln=True, fill=True)
                    current_cat = row[7]

                pdf.set_font("PolishArial", "", 10)
                pdf.cell(0, 8, f"  - {row[1]} | Cena: {row[2]} PLN", ln=True)

            self._save_and_open(pdf, "raport_produkty.pdf")
            return True, "Sukces"
        except Exception as e:
            return False, str(e)

    def raport_statystyka_magazynu(self):
        """Tworzy raport analityczny zawierający wizualizację danych w formie wykresu słupkowego."""
        try:
            # Zliczanie wystąpień produktów w każdej kategorii
            cols, data = db_operations.fetch_all("PRODUKTY")
            counts = {}
            for r in data:
                kat = r[7]
                counts[kat] = counts.get(kat, 0) + 1

            # Konfiguracja wykresu w bibliotece Matplotlib
            plt.figure(figsize=(11, 8))
            plt.bar(counts.keys(), counts.values(), color='orange')
            plt.title("Liczba produktów w kategoriach", fontsize=14,
                      fontweight='bold')
            plt.ylabel("Ilość sztuk")

            # Formatowanie osi Y: wymuszenie wyświetlania tylko liczb całkowitych
            plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))

            # Formatowanie osi X: pionowy obrót etykiet w celu uniknięcia nakładania się tekstu
            plt.xticks(rotation=90)
            plt.tight_layout()

            # Zapis grafiki do pliku tymczasowego przed osadzeniem w PDF
            chart_path = os.path.join(self.output_dir, "raport_produkty_wykres.png")
            plt.savefig(chart_path)
            plt.close()

            pdf = self._setup_pdf()
            pdf.set_font("PolishArial", "B", 20)
            pdf.cell(0, 20, "Statystyka Kategorii", ln=True, align='C')

            # Osadzenie wygenerowanego wykresu w dokumencie PDF
            pdf.image(chart_path, x=10, y=40, w=190)

            self._save_and_open(pdf, "raport_wykres_magazynu.pdf")
            return True, "Sukces"
        except Exception as e:
            return False, str(e)

    def raport_karta_klienta(self, nazwisko_klienta):
        """Generuje kartę informacyjną wybranego klienta."""
        try:
            cols, data = db_operations.fetch_all("KLIENCI")
            # Wyszukiwanie klienta na podstawie frazy nazwiska (kryterium wyszukiwania)
            klient = next((r for r in data if
                           nazwisko_klienta.lower() in str(r[2]).lower()),
                          None)

            pdf = self._setup_pdf()
            # Rysowanie ramki
            pdf.rect(10, 10, 190, 80)
            pdf.set_font("PolishArial", "B", 14)
            pdf.cell(0, 15, "KARTA INFORMACYJNA KLIENTA", ln=True, align='C')

            pdf.set_font("PolishArial", "", 12)
            if klient:
                pdf.ln(5)
                pdf.cell(0, 10, f"ID Klienta: {klient[0]}", ln=True)
                pdf.cell(0, 10, f"Imię i Nazwisko: {klient[1]} {klient[2]}",
                         ln=True)
                pdf.cell(0, 10, f"Email: {klient[4]}", ln=True)
                pdf.cell(0, 10, f"Telefon: {klient[3]}", ln=True)
            else:
                pdf.cell(0, 10, "Nie znaleziono klienta o podanym nazwisku.",
                         ln=True)

            self._save_and_open(pdf, "raport_formularz_klienta.pdf")
            return True, "Sukces"
        except Exception as e:
            return False, str(e)

    def raport_lista_dostawcow(self):
        """Generuje przejrzyste zestawienie wszystkich dostawców zapisanych w bazie danych."""
        try:
            cols, data = db_operations.fetch_all("DOSTAWCY")
            pdf = self._setup_pdf()
            pdf.set_font("PolishArial", "B", 14)
            pdf.cell(0, 10, "LISTA DOSTAWCÓW", ln=True)
            pdf.ln(5)

            pdf.set_font("PolishArial", "", 10)
            for r in data:
                # Wyświetlanie danych
                pdf.cell(0, 8, f"Firma: {r[1]} (NIP: {r[2]}) - Tel: {r[3]}",
                         ln=True, border='B')

            self._save_and_open(pdf, "lista_dostawcow.pdf")
            return True, "Sukces"
        except Exception as e:
            return False, str(e)
