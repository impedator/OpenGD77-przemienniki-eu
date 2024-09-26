
## OpenGD77 - Przemienniki.eu

Ten skrypt pobiera dane o przemiennikach z serwisu [przemienniki.eu](https://przemienniki.eu), filtruje je według trybów (np. DMR, FM), i generuje pliki CSV z szczegółowymi informacjami o przemiennikach.

### Zawartość projektu

- **skrypt**: Skrypt Python do pobierania i przetwarzania danych z przemienniki.eu.
- **convert.yaml**: Plik konfiguracyjny, który można dostosować według własnych potrzeb.

### Instrukcja

1. **Klonowanie repozytorium**

   Aby sklonować repozytorium, użyj następującego polecenia:
   ```bash
   git clone https://github.com/impedator/OpenGD77-przemienniki-eu.git
   cd OpenGD77-przemienniki-eu
   ```

2. **Dostosowanie pliku konfiguracyjnego**

   Zaktualizuj plik `convert.yaml`, aby dopasować go do swoich wymagań (np. strefy, parametry zapytań).

3. **Uruchomienie skryptu**

   Skrypt można uruchomić w środowisku Python, aby wygenerować pliki CSV:
   ```bash
   python your_script.py
   ```

### Wymagania

- Python 3.x
- Biblioteki Python: `requests`, `geopy`, `yaml`

Aby zainstalować wymagane biblioteki, użyj:
```bash
pip install requests geopy pyyaml
```

### Wyniki

Skrypt generuje dwa pliki CSV:

1. **channels.csv** – Zawiera szczegółowe informacje o przemiennikach, takie jak:
   - Numer kanału
   - Nazwa kanału (np. `SR7T-Digi` lub `SR7T-FM`)
   - Częstotliwość RX i TX
   - Typ kanału (Cyfrowy lub Analogowy)
   - Kody kolorów, czasy nadawania, i inne dane techniczne

2. **zones.csv** – Zawiera informacje o strefach (zones), w których znajdują się przemienniki, na podstawie pliku `convert.yaml`.

### Przykład pliku `convert.yaml`

Plik `convert.yaml` zawiera informacje o strefach i parametrach zapytania, np.:

```yaml
Country: Poland
Zones:
  Krakow:
    Latitude: 50.0412773
    Longitude: 19.9476007
    MaxDistance: 100
  Warszawa:
    Latitude: 52.2198423
    Longitude: 21.0359520
    MaxDistance: 150
```

### Struktura pliku `channels.csv`

Plik `channels.csv` zawiera następujące kolumny:

1. **Numer kanału**
2. **Nazwa kanału**
3. **Typ kanału** (Cyfrowy lub Analogowy)
4. **Częstotliwość RX** (z przecinkiem, np. `438,875`)
5. **Częstotliwość TX**
6. **Szerokość pasma (kHz)** (dla analogowych 12,5 kHz)
7. **Kod koloru** (dla cyfrowych)
8. **Czas nadawania (TOT)**
9. **Szczegóły lokalizacji (szerokość i długość geograficzna)**

### Licencja

Projekt jest dostępny na licencji [MIT](LICENSE).

---

### Słowniczek

- **Przemiennik** – Urządzenie, które odbiera sygnał radiowy na jednej częstotliwości i nadaje na innej.
- **DMR** – Cyfrowa komunikacja radiowa (Digital Mobile Radio).
- **FM** – Analogowa transmisja częstotliwości radiowej (Frequency Modulation).

