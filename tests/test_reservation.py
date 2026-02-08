"""
Testy jednostkowe dla modułu reservation.
Testuje klasy Reservation i ReservationManager odpowiedzialne za tworzenie,
zarządzanie i anulowanie rezerwacji pokojów hotelowych.

"""

import unittest
from datetime import date, timedelta
from unittest.mock import Mock

from src.hotel import Hotel, Room
from src.reservation import Reservation, ReservationManager
from src.user import User


class TestReservation(unittest.TestCase):
    """Testy dla klasy Reservation"""

    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        self.today = date.today()
        self.start_date = self.today + timedelta(days=1)
        self.end_date = self.today + timedelta(days=4)
        self.reservation = Reservation(
            reservation_id="R1",
            hotel_id="H1",
            room_id="RM1",
            user_id="U1",
            start_date=self.start_date,
            end_date=self.end_date,
            total_price=300.0
        )

    def test_book_room_with_insufficient_capacity(self):
        """Test rezerwacji pokoju z niewystarczającą pojemnością"""
        hotel = Hotel("H1", "Test Hotel", "Warszawa", 4)
        room = Room("R1", 101, "standard", 200, 2)  # Pojemność 2 osoby
        hotel.add_room(room)

        available_rooms = hotel.get_available_rooms(
            start_date=date.today() + timedelta(days=1),
            end_date=date.today() + timedelta(days=3),
            capacity=3  # Wymagana pojemność 3
        )

        self.assertEqual(len(available_rooms), 0)

    def test_reservation_initialization(self):
        """Test poprawnej inicjalizacji rezerwacji"""
        self.assertEqual(self.reservation.reservation_id, "R1")
        self.assertEqual(self.reservation.hotel_id, "H1")
        self.assertEqual(self.reservation.room_id, "RM1")
        self.assertEqual(self.reservation.user_id, "U1")
        self.assertEqual(self.reservation.start_date, self.start_date)
        self.assertEqual(self.reservation.end_date, self.end_date)
        self.assertEqual(self.reservation.total_price, 300.0)
        self.assertEqual(self.reservation.status, "confirmed")

    def test_reservation_initialization_invalid_dates(self):
        """Test inicjalizacji rezerwacji z nieprawidłowymi datami"""
        with self.assertRaises(ValueError):
            Reservation(
                reservation_id="R1",
                hotel_id="H1",
                room_id="RM1",
                user_id="U1",
                start_date=self.end_date,  # Data zakończenia przed rozpoczęciem
                end_date=self.start_date,
                total_price=300.0
            )

        with self.assertRaises(ValueError):
            Reservation(
                reservation_id="R1",
                hotel_id="H1",
                room_id="RM1",
                user_id="U1",
                start_date=self.today,  # Te same daty
                end_date=self.today,
                total_price=300.0
            )

    def test_create_reservation_success(self):
        """Test tworzenia rezerwacji z powodzeniem"""
        # Przygotowanie makiet obiektów
        mock_hotel = Mock(spec=Hotel)
        mock_hotel.hotel_id = "H1"

        mock_room = Mock(spec=Room)
        mock_room.room_id = "RM1"
        mock_room.price = 100.0
        mock_room.is_available.return_value = True
        mock_room.add_booking.return_value = None

        mock_user = Mock(spec=User)
        mock_user.user_id = "U1"

        # Wykonanie testu
        reservation = Reservation.create(
            hotel=mock_hotel,
            room=mock_room,
            user=mock_user,
            start_date=self.start_date,
            end_date=self.end_date
        )

        # Weryfikacja
        self.assertIsInstance(reservation, Reservation)
        self.assertEqual(reservation.hotel_id, "H1")
        self.assertEqual(reservation.room_id, "RM1")
        self.assertEqual(reservation.user_id, "U1")
        self.assertEqual(reservation.start_date, self.start_date)
        self.assertEqual(reservation.end_date, self.end_date)
        self.assertEqual(reservation.total_price, 300.0)  # 3 dni * 100.0 za noc
        self.assertEqual(reservation.status, "confirmed")

        # Sprawdzenie, czy metody z makiety zostały wywołane
        mock_room.is_available.assert_called_once_with(self.start_date, self.end_date)
        mock_room.add_booking.assert_called_once_with(self.start_date, self.end_date)

    def test_create_reservation_room_unavailable(self):
        """Test tworzenia rezerwacji gdy pokój jest niedostępny"""
        # Przygotowanie makiet obiektów
        mock_hotel = Mock(spec=Hotel)
        mock_room = Mock(spec=Room)
        mock_room.number = 101
        mock_room.is_available.return_value = False
        mock_user = Mock(spec=User)

        # Wykonanie testu
        with self.assertRaises(ValueError):
            Reservation.create(
                hotel=mock_hotel,
                room=mock_room,
                user=mock_user,
                start_date=self.start_date,
                end_date=self.end_date
            )

        # Sprawdzenie, czy metody z makiety zostały wywołane
        mock_room.is_available.assert_called_once_with(self.start_date, self.end_date)
        mock_room.add_booking.assert_not_called()


    def test_cancel_reservation_success(self):
        """Test anulowania rezerwacji z powodzeniem"""
        mock_room = Mock(spec=Room)
        mock_room.remove_booking.return_value = True

        result = self.reservation.cancel(mock_room)

        self.assertTrue(result)
        self.assertEqual(self.reservation.status, "cancelled")
        mock_room.remove_booking.assert_called_once_with(self.start_date, self.end_date)

    def test_cancel_reservation_already_cancelled(self):
        """Test anulowania już anulowanej rezerwacji"""
        mock_room = Mock(spec=Room)

        # Najpierw anuluj rezerwację
        self.reservation.status = "cancelled"

        result = self.reservation.cancel(mock_room)

        self.assertFalse(result)
        self.assertEqual(self.reservation.status, "cancelled")
        mock_room.remove_booking.assert_not_called()

    def test_cancel_completed_reservation(self):
        """Test anulowania zakończonej rezerwacji"""
        mock_room = Mock(spec=Room)

        # Oznacz rezerwację jako zakończoną
        self.reservation.status = "completed"

        result = self.reservation.cancel(mock_room)

        self.assertFalse(result)
        self.assertEqual(self.reservation.status, "completed")  # Status się nie zmienia
        mock_room.remove_booking.assert_not_called()  # Metoda nie jest wywoływana

    def test_calculate_nights(self):
        """Test obliczania liczby nocy w rezerwacji"""
        # Rezerwacja na 3 dni (4 - 1)
        self.assertEqual(self.reservation.calculate_nights(), 3)

        # Rezerwacja na 1 dzień
        reservation = Reservation(
            reservation_id="R2",
            hotel_id="H1",
            room_id="RM1",
            user_id="U1",
            start_date=self.today,
            end_date=self.today + timedelta(days=1),
            total_price=100.0
        )
        self.assertEqual(reservation.calculate_nights(), 1)

        # Rezerwacja na 7 dni
        reservation = Reservation(
            reservation_id="R3",
            hotel_id="H1",
            room_id="RM1",
            user_id="U1",
            start_date=self.today,
            end_date=self.today + timedelta(days=7),
            total_price=700.0
        )
        self.assertEqual(reservation.calculate_nights(), 7)

    def test_calculate_nights_extended_stays(self):
        """Test obliczania liczby nocy dla dłuższych pobytów"""
        # Rezerwacja na 14 dni
        reservation = Reservation(
            reservation_id="R4",
            hotel_id="H1",
            room_id="RM1",
            user_id="U1",
            start_date=self.today,
            end_date=self.today + timedelta(days=14),
            total_price=1400.0
        )
        self.assertEqual(reservation.calculate_nights(), 14)


class TestReservationManager(unittest.TestCase):
    """Testy dla klasy ReservationManager"""

    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        self.manager = ReservationManager()
        self.today = date.today()

        # Przygotowanie przykładowych rezerwacji
        self.reservation1 = Reservation(
            reservation_id="R1",
            hotel_id="H1",
            room_id="RM1",
            user_id="U1",
            start_date=self.today + timedelta(days=1),
            end_date=self.today + timedelta(days=4),
            total_price=300.0
        )

        self.reservation2 = Reservation(
            reservation_id="R2",
            hotel_id="H1",
            room_id="RM2",
            user_id="U2",
            start_date=self.today + timedelta(days=5),
            end_date=self.today + timedelta(days=8),
            total_price=400.0
        )

        self.reservation3 = Reservation(
            reservation_id="R3",
            hotel_id="H2",
            room_id="RM3",
            user_id="U1",
            start_date=self.today + timedelta(days=10),
            end_date=self.today + timedelta(days=12),
            total_price=200.0
        )

    def test_cancel_non_existing_reservation_in_manager(self):
        """Test anulowania nieistniejącej rezerwacji w menedżerze"""
        mock_hotel = Mock(spec=Hotel)
        mock_hotel.hotel_id = "H1"
        mock_room = Mock(spec=Room)
        mock_room.room_id = "RM1"

        result = self.manager.cancel_reservation("NON_EXISTENT", mock_hotel, mock_room)
        self.assertFalse(result)

    def test_add_reservation_success(self):
        """Test dodawania rezerwacji z powodzeniem"""
        self.manager.add_reservation(self.reservation1)

        self.assertIn("R1", self.manager.reservations)
        self.assertEqual(self.manager.reservations["R1"], self.reservation1)

    def test_add_reservation_duplicate(self):
        """Test dodawania rezerwacji o istniejącym ID"""
        self.manager.add_reservation(self.reservation1)

        with self.assertRaises(ValueError):
            self.manager.add_reservation(self.reservation1)

    def test_get_reservation_existing(self):
        """Test pobierania istniejącej rezerwacji"""
        self.manager.add_reservation(self.reservation1)

        retrieved_reservation = self.manager.get_reservation("R1")
        self.assertEqual(retrieved_reservation, self.reservation1)

    def test_get_reservation_non_existing(self):
        """Test pobierania nieistniejącej rezerwacji"""
        retrieved_reservation = self.manager.get_reservation("R999")
        self.assertIsNone(retrieved_reservation)

    def test_get_user_reservations(self):
        """Test pobierania rezerwacji użytkownika"""
        self.manager.add_reservation(self.reservation1)
        self.manager.add_reservation(self.reservation2)
        self.manager.add_reservation(self.reservation3)

        # Użytkownik U1 ma rezerwacje R1 i R3
        user_reservations = self.manager.get_user_reservations("U1")
        self.assertEqual(len(user_reservations), 2)
        self.assertIn(self.reservation1, user_reservations)
        self.assertIn(self.reservation3, user_reservations)

        # Użytkownik U2 ma tylko rezerwację R2
        user_reservations = self.manager.get_user_reservations("U2")
        self.assertEqual(len(user_reservations), 1)
        self.assertIn(self.reservation2, user_reservations)

        # Użytkownik U3 nie ma rezerwacji
        user_reservations = self.manager.get_user_reservations("U3")
        self.assertEqual(len(user_reservations), 0)

    def test_get_hotel_reservations(self):
        """Test pobierania rezerwacji hotelu"""
        self.manager.add_reservation(self.reservation1)
        self.manager.add_reservation(self.reservation2)
        self.manager.add_reservation(self.reservation3)

        # Hotel H1 ma rezerwacje R1 i R2
        hotel_reservations = self.manager.get_hotel_reservations("H1")
        self.assertEqual(len(hotel_reservations), 2)
        self.assertIn(self.reservation1, hotel_reservations)
        self.assertIn(self.reservation2, hotel_reservations)

        # Hotel H2 ma tylko rezerwację R3
        hotel_reservations = self.manager.get_hotel_reservations("H2")
        self.assertEqual(len(hotel_reservations), 1)
        self.assertIn(self.reservation3, hotel_reservations)

        # Hotel H3 nie ma rezerwacji
        hotel_reservations = self.manager.get_hotel_reservations("H3")
        self.assertEqual(len(hotel_reservations), 0)

    def test_cancel_reservation_success(self):
        """Test anulowania rezerwacji z powodzeniem"""
        self.manager.add_reservation(self.reservation1)

        mock_hotel = Mock(spec=Hotel)
        # Ustawienie właściwości hotel_id dla mocka hotelu, aby pasował do rezerwacji
        mock_hotel.hotel_id = "H1"

        mock_room = Mock(spec=Room)
        # Ustawienie właściwości room_id dla mocka pokoju, aby pasował do rezerwacji
        mock_room.room_id = "RM1"
        mock_room.remove_booking.return_value = True

        result = self.manager.cancel_reservation("R1", mock_hotel, mock_room)

        self.assertTrue(result)
        self.assertEqual(self.reservation1.status, "cancelled")
        mock_room.remove_booking.assert_called_once_with(
            self.reservation1.start_date,
            self.reservation1.end_date
        )

    def test_cancel_reservation_non_existing(self):
        """Test anulowania nieistniejącej rezerwacji"""
        mock_hotel = Mock(spec=Hotel)
        mock_room = Mock(spec=Room)

        result = self.manager.cancel_reservation("R999", mock_hotel, mock_room)

        self.assertFalse(result)
        mock_room.remove_booking.assert_not_called()

    def test_cancel_reservation_mismatched_hotel(self):
        """Test anulowania rezerwacji z niepasującym ID hotelu"""
        self.manager.add_reservation(self.reservation1)

        mock_hotel = Mock(spec=Hotel)
        mock_hotel.hotel_id = "H2"  # Różny od H1 w reservation1

        mock_room = Mock(spec=Room)
        mock_room.room_id = "RM1"

        with self.assertRaises(ValueError):
            self.manager.cancel_reservation("R1", mock_hotel, mock_room)

    def test_cancel_reservation_mismatched_room(self):
        """Test anulowania rezerwacji z niepasującym ID pokoju"""
        self.manager.add_reservation(self.reservation1)

        mock_hotel = Mock(spec=Hotel)
        mock_hotel.hotel_id = "H1"

        mock_room = Mock(spec=Room)
        mock_room.room_id = "RM2"  # Różny od RM1 w reservation1

        with self.assertRaises(ValueError):
            self.manager.cancel_reservation("R1", mock_hotel, mock_room)


if __name__ == '__main__':
    unittest.main()