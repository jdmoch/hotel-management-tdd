# System Zarządzania Hotelem

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Coverage](https://img.shields.io/badge/coverage-99%25-yellowgreen)
![License](https://img.shields.io/badge/license-MIT-green)

System rezerwacji pokoi hotelowych stworzony w języku Python jako projekt zaliczeniowy.

## Funkcjonalności
- **Zarządzanie hotelami**
  - Tworzenie pokoi z różnymi parametrami
  - Wyszukiwanie hoteli po lokalizacji i ocenie
  - Sprawdzanie dostępności pokoi w kalendarzu
  
- **Rezerwacje**
  - Automatyczne obliczanie kosztów pobytu
  - Anulowanie rezerwacji z aktualizacją dostępności
  - Historia rezerwacji dla użytkowników

- **Bezpieczeństwo**
  - Haszowanie haseł z SHA-256
  - Walidacja danych wejściowych (e-mail, telefon)
  - System uwierzytelniania użytkowników

## Struktura Projektu
```
projekt/
├── src/
│   ├── __init__.py
│   ├── hotel.py            # Zarządzanie hotelami i pokojami
│   ├── reservation.py      # Obsługa rezerwacji
│   └── user.py             # Obsługa użytkowników
├── tests/
│   ├── __init__.py
│   ├── test_hotel.py
│   ├── test_reservation.py
│   └── test_user.py
├── requirements.txt
└── README.md
```

## Instalacja

1. Sklonuj repozytorium
2. Zainstaluj zależności:

```bash
pip install -r requirements.txt
```

## Uruchamianie Testów

Uruchom wszystkie testy za pomocą:

```bash

pytest

```

### Pokrycie Kodu

Projekt ma wysokie pokrycie kodu testami:

```
Name                        Stmts   Miss  Cover
-----------------------------------------------
src\__init__.py                 0      0   100%
src\hotel.py                   77      2    97%
src\reservation.py             56      1    98%
src\user.py                   112      4    96%
tests\__init__.py               0      0   100%
tests\test_hotel.py           192      1    99%
tests\test_reservation.py     183      1    99%
tests\test_user.py            242      1    99%
-----------------------------------------------
TOTAL                         862     10    99%

```

Aby uruchomić testy z raportami pokrycia kodu:

```bash
coverage run -m pytest
coverage report
coverage html  # Raport w HTML: htmlcov/index.html
```

## Przykłady Użycia

### Zarządzanie hotelem

```python
from src.hotel import Hotel, Room
from datetime import date

room = Room(
    room_id="101",
    number=101,
    room_type="Deluxe",
    price=299.99,
    capacity=4
)

hotel = Hotel(
    hotel_id="H1",
    name="Grand Hotel",
    address="Kraków, Rynek Główny 1",
    star_rating=5
)
hotel.add_room(room)
```

### Rezerwacja pokoju

```python
from src.reservation import Reservation
from src.user import UserManager

manager = UserManager()
user = manager.register_user(
    first_name="Jan",
    last_name="Kowalski",
    email="jan@example.com",
    phone="+48123456789",
    password="SecurePass123!"
)

reservation = Reservation.create(
    hotel=hotel,
    room=room,
    user=user,
    start_date=date(2024, 1, 1),
    end_date=date(2024, 1, 5)
)

print(f"Koszt rezerwacji: {reservation.total_price} PLN")
```

## Moduły

### hotel.py
- `Room` – Reprezentuje pokój hotelowy
- `Hotel` – Zarządza pokojami, rezerwacjami, dostępnością
- `HotelDatabase` – Baza danych hoteli, wyszukiwanie

### reservation.py
- `Reservation` – Tworzenie, anulowanie i obsługa rezerwacji
- `ReservationManager` – Rejestracja i zarządzanie rezerwacjami

### user.py
- `User` – Rejestracja użytkowników, haszowanie, walidacja danych
- `UserManager` – Uwierzytelnianie i wyszukiwanie użytkowników
