"""
Moduł zarządzający rezerwacjami pokoi hotelowych.
Zawiera klasy do tworzenia, modyfikowania i anulowania rezerwacji.

"""

from datetime import date
from typing import Dict, List, Optional
import uuid

from src.hotel import Hotel, Room
from src.user import User


class Reservation:
    """Klasa reprezentująca rezerwację pokoju hotelowego."""

    def __init__(self, reservation_id: str, hotel_id: str, room_id: str,
                 user_id: str, start_date: date, end_date: date, total_price: float):
        """
        Inicjalizuje nową rezerwację.

        Args:
            reservation_id: Unikalny identyfikator rezerwacji
            hotel_id: Identyfikator hotelu
            room_id: Identyfikator pokoju
            user_id: Identyfikator użytkownika
            start_date: Data rozpoczęcia pobytu
            end_date: Data zakończenia pobytu
            total_price: Całkowita cena rezerwacji

        Raises:
            ValueError: Gdy data rozpoczęcia jest późniejsza lub równa dacie zakończenia
        """
        if start_date >= end_date:
            raise ValueError("Data rozpoczęcia musi być wcześniejsza niż data zakończenia")

        self.reservation_id = reservation_id
        self.hotel_id = hotel_id
        self.room_id = room_id
        self.user_id = user_id
        self.start_date = start_date
        self.end_date = end_date
        self.total_price = total_price
        self.status = "confirmed"  # "confirmed", "cancelled", "completed"

    @classmethod
    def create(cls, hotel: Hotel, room: Room, user: User,
               start_date: date, end_date: date) -> 'Reservation':
        """
        Tworzy nową rezerwację.

        Args:
            hotel: Obiekt hotelu
            room: Obiekt pokoju
            user: Obiekt użytkownika
            start_date: Data rozpoczęcia pobytu
            end_date: Data zakończenia pobytu

        Returns:
            Nowy obiekt rezerwacji

        Raises:
            ValueError: Gdy pokój nie jest dostępny w danym terminie
        """
        # Sprawdź poprawność dat
        if start_date >= end_date:
            raise ValueError("Data rozpoczęcia musi być wcześniejsza niż data zakończenia")

        # Sprawdź dostępność pokoju
        if not room.is_available(start_date, end_date):
            raise ValueError(f"Pokój {room.number} nie jest dostępny w wybranym terminie")

        # Oblicz całkowitą cenę
        days = (end_date - start_date).days
        total_price = days * room.price

        # Utwórz ID rezerwacji
        reservation_id = str(uuid.uuid4())

        # Utwórz obiekt rezerwacji
        reservation = cls(
            reservation_id=reservation_id,
            hotel_id=hotel.hotel_id,
            room_id=room.room_id,
            user_id=user.user_id,
            start_date=start_date,
            end_date=end_date,
            total_price=total_price
        )

        # Dodaj rezerwację do listy zajętych terminów pokoju
        room.add_booking(start_date, end_date)

        return reservation

    def cancel(self, room: Room) -> bool:
        """
        Anuluje rezerwację.

        Args:
            room: Obiekt pokoju, którego dotyczy rezerwacja

        Returns:
            True jeśli anulowanie powiodło się, False w przeciwnym przypadku
        """
        if self.status == "confirmed":
            self.status = "cancelled"
            # Usuń rezerwację z listy zajętych terminów pokoju
            return room.remove_booking(self.start_date, self.end_date)
        return False

    def calculate_nights(self) -> int:
        """
        Oblicza liczbę nocy w rezerwacji.

        Returns:
            Liczba nocy
        """
        return (self.end_date - self.start_date).days


class ReservationManager:
    """Klasa zarządzająca rezerwacjami."""

    def __init__(self):
        """Inicjalizuje nowy menedżer rezerwacji."""
        self.reservations: Dict[str, Reservation] = {}

    def add_reservation(self, reservation: Reservation) -> None:
        """
        Dodaje rezerwację do systemu.

        Args:
            reservation: Obiekt rezerwacji do dodania

        Raises:
            ValueError: Gdy rezerwacja o danym ID już istnieje
        """
        if reservation.reservation_id in self.reservations:
            raise ValueError(f"Rezerwacja o ID {reservation.reservation_id} już istnieje")

        self.reservations[reservation.reservation_id] = reservation

    def get_reservation(self, reservation_id: str) -> Optional[Reservation]:
        """
        Zwraca rezerwację o danym ID lub None.

        Args:
            reservation_id: Identyfikator rezerwacji

        Returns:
            Obiekt rezerwacji lub None, jeśli nie znaleziono
        """
        return self.reservations.get(reservation_id)

    def get_user_reservations(self, user_id: str) -> List[Reservation]:
        """
        Zwraca listę rezerwacji danego użytkownika.

        Args:
            user_id: Identyfikator użytkownika

        Returns:
            Lista rezerwacji użytkownika
        """
        return [
            reservation for reservation in self.reservations.values()
            if reservation.user_id == user_id
        ]

    def get_hotel_reservations(self, hotel_id: str) -> List[Reservation]:
        """
        Zwraca listę rezerwacji dla danego hotelu.

        Args:
            hotel_id: Identyfikator hotelu

        Returns:
            Lista rezerwacji hotelu
        """
        return [
            reservation for reservation in self.reservations.values()
            if reservation.hotel_id == hotel_id
        ]

    def cancel_reservation(self, reservation_id: str, hotel: Hotel, room: Room) -> bool:
        """
        Anuluje rezerwację o danym ID.

        Args:
            reservation_id: Identyfikator rezerwacji
            hotel: Obiekt hotelu, którego dotyczy rezerwacja
            room: Obiekt pokoju, którego dotyczy rezerwacja

        Returns:
            True jeśli anulowanie powiodło się, False w przeciwnym przypadku
        """
        reservation = self.get_reservation(reservation_id)
        if reservation:
            if reservation.hotel_id != hotel.hotel_id or reservation.room_id != room.room_id:
                raise ValueError("Podany hotel lub pokój nie pasują do rezerwacji")
            return reservation.cancel(room)

        return False
