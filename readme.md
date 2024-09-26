
## OpenGD77 - Przemienniki.eu

Ten skrypt pobiera dane o przemiennikach z serwisu [przemienniki.eu](https://przemienniki.eu), filtruje je według trybów (np. DMR, FM), i generuje pliki CSV kompatybilne z OpenGD77 CPS.

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
   python convert.py
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

1. **channels.csv**
2. **zones.csv**

zawartość plików można zaimportować w oprogramowaniu OpenGD77 CPS

### Przykład pliku `convert.yaml`

Plik `convert.yaml` zawiera informacje o strefach i parametrach zapytania, np.:

```yaml
Country: Poland
QueryParams:
  Band: "70cm,2m"
  Mode: "fm,dmr"
  Prefix: "sr9"
  Status: "working"
  Distance: "100"
Zones:
  Krakow:
    Latitude: 50.0412773
    Longitude: 19.9476007
    MaxDistance: 100
  Warszawa:
    Latitude: 52.2198423
    Longitude: 21.0359520
    MaxDistance: 150
  BialaPodl:
    Latitude: 52.0287157
    Longitude: 23.1226839
    MaxDistance: 100
```

### Licencja

Projekt jest dostępny na licencji [MIT](LICENSE).

---

### Słowniczek

- **Przemiennik** – Urządzenie, które odbiera sygnał radiowy na jednej częstotliwości i nadaje na innej.
- **DMR** – Cyfrowa komunikacja radiowa (Digital Mobile Radio).
- **FM** – Analogowa transmisja częstotliwości radiowej (Frequency Modulation).

