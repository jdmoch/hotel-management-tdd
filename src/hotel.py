"""
Moduł zarządzający systemem pokoi hotelowych.
Zawiera klasy do obsługi pokoi, hoteli oraz wyszukiwania dostępności.

"""

from datetime import date
from typing import List, Dict, Optional, Tuple


class Room:
    """Klasa reprezentująca pokój hotelowy."""

    def __init__(self, room_id: str, number: int, room_type: str, price: float, capacity: int):
        """
        Inicjalizuje nowy pokój hotelowy.

        Args:
            room_id: Unikalny identyfikator pokoju
            number: Numer pokoju
            room_type: Typ pokoju (np. "standard", "deluxe", "suite")
            price: Cena za jedną dobę
            capacity: Maksymalna liczba osób
        """
        self.room_id = room_id
        self.number = number
        self.room_type = room_type
        self.price = price
        self.capacity = capacity
        self.booked_dates: List[Tuple[date, date]] = []  # lista krotek (start_date, end_date)

    def is_available(self, start_date: date, end_date: date) -> bool:
        """
        Sprawdza czy pokój jest dostępny w danym terminie.

        Args:
            start_date: Data rozpoczęcia pobytu
            end_date: Data zakończenia pobytu

        Returns:
            True jeśli pokój jest dostępny, False w przeciwnym przypadku
        """
        if start_date >= end_date:
            raise ValueError("Data rozpoczęcia musi być wcześniejsza niż data zakończenia")

        for booked_start, booked_end in self.booked_dates:
            if not (end_date <= booked_start or start_date >= booked_end):
                return False
        return True

    def add_booking(self, start_date: date, end_date: date) -> None:
        """
        Dodaje rezerwację do listy zajętych terminów.

        Args:
            start_date: Data rozpoczęcia pobytu
            end_date: Data zakończenia pobytu

        Raises:
            ValueError: Gdy pokój jest już zarezerwowany w danym terminie
        """
        if start_date >= end_date:
            raise ValueError("Data rozpoczęcia musi być wcześniejsza niż data zakończenia")

        if not self.is_available(start_date, end_date):
            raise ValueError(f"Pokój {self.number} jest już zarezerwowany w tym terminie")
        self.booked_dates.append((start_date, end_date))

    def remove_booking(self, start_date: date, end_date: date) -> bool:
        """
        Usuwa rezerwację z listy zajętych terminów.

        Args:
            start_date: Data rozpoczęcia pobytu
            end_date: Data zakończenia pobytu

        Returns:
            True jeśli rezerwacja została usunięta, False gdy nie znaleziono takiej rezerwacji
        """
        booking = (start_date, end_date)
        if booking in self.booked_dates:
            self.booked_dates.remove(booking)
            return True
        return False


class Hotel:
    """Klasa reprezentująca hotel."""

    def __init__(self, hotel_id: str, name: str, address: str, star_rating: int):
        """
        Inicjalizuje nowy hotel.

        Args:
            hotel_id: Unikalny identyfikator hotelu
            name: Nazwa hotelu
            address: Adres hotelu
            star_rating: Ocena hotelu w gwiazdkach (1-5)

        Raises:
            ValueError: Gdy ocena hotelu jest poza zakresem 1-5
        """
        if not 1 <= star_rating <= 5:
            raise ValueError("Ocena hotelu musi być od 1 do 5 gwiazdek")

        self.hotel_id = hotel_id
        self.name = name
        self.address = address
        self.star_rating = star_rating
        self.rooms: Dict[str, Room] = {}  # słownik {room_id: Room}

    def add_room(self, room: Room) -> None:
        """
        Dodaje pokój do hotelu.

        Args:
            room: Obiekt pokoju do dodania

        Raises:
            ValueError: Gdy pokój o danym ID już istnieje w hotelu
        """
        if room.room_id in self.rooms:
            raise ValueError(f"Pokój o ID {room.room_id} już istnieje w hotelu")
        self.rooms[room.room_id] = room

    def get_room(self, room_id: str) -> Optional[Room]:
        """
        Zwraca pokój o danym ID lub None.

        Args:
            room_id: Identyfikator pokoju

        Returns:
            Obiekt pokoju lub None, jeśli nie znaleziono
        """
        return self.rooms.get(room_id)

    def get_available_rooms(self, start_date: date, end_date: date, capacity: int = 1) -> List[Room]:

        """
        Zwraca listę dostępnych pokoi w danym terminie.

        Args:
            start_date: Data rozpoczęcia pobytu
            end_date: Data zakończenia pobytu
            capacity: Minimalna wymagana pojemność pokoju (ilość osób)

        Returns:
            Lista dostępnych pokoi spełniających kryteria
        """
        if start_date >= end_date:
            raise ValueError("Data rozpoczęcia musi być wcześniejsza niż data zakończenia")

        available_rooms = []
        for room in self.rooms.values():
            if room.is_available(start_date, end_date) and room.capacity >= capacity:
                available_rooms.append(room)
        return available_rooms

    def book_room(self, room_id: str, start_date: date, end_date: date) -> bool:
        """
        Rezerwuje pokój o danym ID w podanym terminie.

        Args:
            room_id: Identyfikator pokoju
            start_date: Data rozpoczęcia pobytu
            end_date: Data zakończenia pobytu

        Returns:
            True jeśli rezerwacja się powiodła, False w przeciwnym przypadku
        """
        if start_date >= end_date:
            raise ValueError("Data rozpoczęcia musi być wcześniejsza niż data zakończenia")

        room = self.get_room(room_id)
        if room and room.is_available(start_date, end_date):
            room.add_booking(start_date, end_date)
            return True
        return False


class HotelDatabase:
    """Klasa zarządzająca bazą hoteli."""

    def __init__(self):
        """Inicjalizuje nową bazę hoteli."""
        self.hotels: Dict[str, Hotel] = {}

    def add_hotel(self, hotel: Hotel) -> None:
        """
        Dodaje hotel do bazy.

        Args:
            hotel: Obiekt hotelu do dodania

        Raises:
            ValueError: Gdy hotel o danym ID już istnieje w bazie
        """
        if hotel.hotel_id in self.hotels:
            raise ValueError(f"Hotel o ID {hotel.hotel_id} już istnieje w bazie")
        self.hotels[hotel.hotel_id] = hotel

    def get_hotel(self, hotel_id: str) -> Optional[Hotel]:
        """
        Zwraca hotel o danym ID lub None.

        Args:
            hotel_id: Identyfikator hotelu

        Returns:
            Obiekt hotelu lub None, jeśli nie znaleziono
        """
        return self.hotels.get(hotel_id)

    def search_hotels(self, location: str = "", min_rating: int = 1) -> List[Hotel]:
        """
        Wyszukuje hotele według lokalizacji i oceny.

        Args:
            location: Fragment adresu do wyszukania (pusty string oznacza dowolną lokalizację)
            min_rating: Minimalna ocena hotelu (1-5)

        Returns:
            Lista hoteli spełniających kryteria
        """
        if not 1 <= min_rating <= 5:
            raise ValueError("Minimalna ocena hotelu musi być od 1 do 5 gwiazdek")

        results = []
        for hotel in self.hotels.values():
            if (location.lower() in hotel.address.lower() and
                    hotel.star_rating >= min_rating):
                results.append(hotel)
        return results
