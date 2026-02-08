"""
Testy jednostkowe dla modułu hotel.
Testuje klasy Room, Hotel i HotelDatabase odpowiedzialne za zarządzanie pokojami,
zarządzanie danymi hoteli oraz wyszukiwanie dostępnych pokoi i hoteli.

"""

import unittest
from datetime import date, timedelta
from src.hotel import Room, Hotel, HotelDatabase


class TestRoom(unittest.TestCase):
    """Testy dla klasy Room"""

    def setUp(self):
        """Przygotowanie przed każdym testem"""
        self.room = Room("R1", 101, "standard", 200, 2)
        self.today = date.today()
        self.tomorrow = self.today + timedelta(days=1)
        self.future_start = self.today + timedelta(days=10)
        self.future_end = self.future_start + timedelta(days=2)

    def test_room_initialization(self):
        """Test poprawnej inicjalizacji pokoju"""
        self.assertEqual(self.room.room_id, "R1")
        self.assertEqual(self.room.number, 101)
        self.assertEqual(self.room.room_type, "standard")
        self.assertEqual(self.room.price, 200)
        self.assertEqual(self.room.capacity, 2)
        self.assertEqual(self.room.booked_dates, [])

    def test_is_available_no_bookings(self):
        """Test dostępności pokoju bez rezerwacji"""
        start = self.today
        end = start + timedelta(days=3)
        self.assertTrue(self.room.is_available(start, end))

    def test_is_available_with_non_overlapping_booking(self):
        """Test dostępności pokoju z niepokrywającą się rezerwacją"""
        # Dodaj rezerwację za 10 dni
        self.room.add_booking(self.future_start, self.future_end)

        # Sprawdź dostępność za tydzień
        check_start = self.today + timedelta(days=7)
        check_end = check_start + timedelta(days=2)
        self.assertTrue(self.room.is_available(check_start, check_end))

    def test_is_available_with_overlapping_booking(self):
        """Test dostępności pokoju z pokrywającą się rezerwacją"""
        # Dodaj rezerwację
        start = self.today + timedelta(days=5)
        end = start + timedelta(days=3)
        self.room.add_booking(start, end)

        # Sprawdź pokrywający się termin
        check_start = start - timedelta(days=1)
        check_end = start + timedelta(days=1)
        self.assertFalse(self.room.is_available(check_start, check_end))

    def test_is_available_exact_dates(self):
        """Test dostępności pokoju na dokładnie te same daty"""
        start = self.today
        end = start + timedelta(days=3)
        self.room.add_booking(start, end)
        self.assertFalse(self.room.is_available(start, end))

    def test_add_booking_success(self):
        """Test dodawania rezerwacji z powodzeniem"""
        start = self.today
        end = start + timedelta(days=3)
        self.room.add_booking(start, end)
        self.assertIn((start, end), self.room.booked_dates)
        self.assertEqual(len(self.room.booked_dates), 1)

    def test_add_booking_overlapping_dates(self):
        """Test dodawania rezerwacji z pokrywającymi się datami"""
        start = self.today
        end = start + timedelta(days=3)
        self.room.add_booking(start, end)

        # Próba dodania pokrywającej się rezerwacji
        with self.assertRaises(ValueError):
            self.room.add_booking(start + timedelta(days=1), end + timedelta(days=1))

    def test_remove_booking_existing(self):
        """Test usuwania istniejącej rezerwacji"""
        start = self.today
        end = start + timedelta(days=3)
        self.room.add_booking(start, end)
        self.assertTrue(self.room.remove_booking(start, end))
        self.assertNotIn((start, end), self.room.booked_dates)
        self.assertEqual(len(self.room.booked_dates), 0)

    def test_remove_booking_non_existing(self):
        """Test usuwania nieistniejącej rezerwacji"""
        start = self.today
        end = start + timedelta(days=3)
        self.assertFalse(self.room.remove_booking(start, end))

    def test_invalid_date_range(self):
        """Test niepoprawnego zakresu dat (początek >= koniec)"""
        start = self.today
        end = start  # Taka sama data
        with self.assertRaises(ValueError):
            self.room.is_available(start, end)

        with self.assertRaises(ValueError):
            later = start + timedelta(days=1)
            self.room.is_available(later, start)  # Początek po końcu


class TestHotel(unittest.TestCase):
    """Testy dla klasy Hotel"""

    def setUp(self):
        """Przygotowanie przed każdym testem"""
        self.hotel = Hotel("H1", "Test Hotel", "Warszawa, ul. Testowa 1", 4)
        self.room1 = Room("R1", 101, "standard", 200, 2)
        self.room2 = Room("R2", 102, "deluxe", 300, 4)
        self.start_date = date.today()
        self.end_date = self.start_date + timedelta(days=3)

    def test_hotel_initialization(self):
        """Test poprawnej inicjalizacji hotelu"""
        self.assertEqual(self.hotel.hotel_id, "H1")
        self.assertEqual(self.hotel.name, "Test Hotel")
        self.assertEqual(self.hotel.address, "Warszawa, ul. Testowa 1")
        self.assertEqual(self.hotel.star_rating, 4)
        self.assertEqual(self.hotel.rooms, {})

    def test_hotel_initialization_invalid_rating(self):
        """Test inicjalizacji hotelu z nieprawidłową oceną"""
        invalid_ratings = [0, 6, -1, 10]
        for rating in invalid_ratings:
            with self.subTest(rating=rating):
                with self.assertRaises(ValueError):
                    Hotel("H1", "Test Hotel", "Warszawa", rating)

    def test_add_room(self):
        """Test dodawania pokoju do hotelu"""
        self.hotel.add_room(self.room1)
        self.assertIn("R1", self.hotel.rooms)
        self.assertEqual(self.hotel.rooms["R1"], self.room1)

    def test_add_room_duplicate(self):
        """Test dodawania pokoju o istniejącym ID"""
        self.hotel.add_room(self.room1)
        room_duplicate = Room("R1", 102, "deluxe", 300, 3)
        with self.assertRaises(ValueError):
            self.hotel.add_room(room_duplicate)

    def test_get_room_existing(self):
        """Test pobierania istniejącego pokoju"""
        self.hotel.add_room(self.room1)
        retrieved_room = self.hotel.get_room("R1")
        self.assertEqual(retrieved_room, self.room1)

    def test_get_room_non_existing(self):
        """Test pobierania nieistniejącego pokoju"""
        retrieved_room = self.hotel.get_room("R1")
        self.assertIsNone(retrieved_room)

    def test_get_available_rooms_all_available(self):
        """Test pobierania dostępnych pokoi gdy wszystkie są dostępne"""
        self.hotel.add_room(self.room1)
        self.hotel.add_room(self.room2)

        available_rooms = self.hotel.get_available_rooms(self.start_date, self.end_date)
        self.assertEqual(len(available_rooms), 2)
        self.assertIn(self.room1, available_rooms)
        self.assertIn(self.room2, available_rooms)

    def test_get_available_rooms_with_capacity(self):
        """Test pobierania dostępnych pokoi z uwzględnieniem pojemności"""
        self.hotel.add_room(self.room1)  # pojemność 2
        self.hotel.add_room(self.room2)  # pojemność 4

        # Sprawdź pokoje dla 3 osób
        available_rooms = self.hotel.get_available_rooms(self.start_date, self.end_date, capacity=3)
        self.assertEqual(len(available_rooms), 1)
        self.assertIn(self.room2, available_rooms)

    def test_get_available_rooms_with_booking(self):
        """Test pobierania dostępnych pokoi z istniejącymi rezerwacjami"""
        self.hotel.add_room(self.room1)
        self.hotel.add_room(self.room2)

        # Zarezerwuj jeden pokój
        self.room1.add_booking(self.start_date, self.end_date)

        available_rooms = self.hotel.get_available_rooms(self.start_date, self.end_date)
        self.assertEqual(len(available_rooms), 1)
        self.assertIn(self.room2, available_rooms)

    def test_book_room_success(self):
        """Test rezerwacji pokoju z powodzeniem"""
        self.hotel.add_room(self.room1)
        self.assertTrue(self.hotel.book_room("R1", self.start_date, self.end_date))
        self.assertFalse(self.room1.is_available(self.start_date, self.end_date))

    def test_book_room_unavailable(self):
        """Test rezerwacji niedostępnego pokoju"""
        self.hotel.add_room(self.room1)

        # Najpierw zarezerwuj pokój
        self.room1.add_booking(self.start_date, self.end_date)

        # Próba rezerwacji już zarezerwowanego pokoju
        self.assertFalse(self.hotel.book_room("R1", self.start_date, self.end_date))

    def test_book_room_non_existing(self):
        """Test rezerwacji nieistniejącego pokoju"""
        self.assertFalse(self.hotel.book_room("R1", self.start_date, self.end_date))

    def test_invalid_date_range_for_available_rooms(self):
        """Test niepoprawnego zakresu dat przy wyszukiwaniu dostępnych pokoi"""
        with self.assertRaises(ValueError):
            self.hotel.get_available_rooms(self.end_date, self.start_date)


class TestHotelDatabase(unittest.TestCase):
    """Testy dla klasy HotelDatabase"""

    def setUp(self):
        """Przygotowanie przed każdym testem"""
        self.db = HotelDatabase()
        self.hotel1 = Hotel("H1", "Hotel Warszawa", "Warszawa, ul. Marszałkowska 1", 4)
        self.hotel2 = Hotel("H2", "Hotel Kraków", "Kraków, ul. Floriańska 1", 5)
        self.hotel3 = Hotel("H3", "Hotel Warszawa Nord", "Warszawa, ul. Mickiewicza 10", 3)

    def test_database_initialization(self):
        """Test poprawnej inicjalizacji bazy hoteli"""
        self.assertEqual(self.db.hotels, {})

    def test_add_hotel(self):
        """Test dodawania hotelu do bazy"""
        self.db.add_hotel(self.hotel1)
        self.assertIn("H1", self.db.hotels)
        self.assertEqual(self.db.hotels["H1"], self.hotel1)

    def test_add_hotel_duplicate(self):
        """Test dodawania hotelu o istniejącym ID"""
        self.db.add_hotel(self.hotel1)
        hotel_duplicate = Hotel("H1", "Test Hotel 2", "Kraków", 5)
        with self.assertRaises(ValueError):
            self.db.add_hotel(hotel_duplicate)

    def test_get_hotel_existing(self):
        """Test pobierania istniejącego hotelu"""
        self.db.add_hotel(self.hotel1)
        retrieved_hotel = self.db.get_hotel("H1")
        self.assertEqual(retrieved_hotel, self.hotel1)

    def test_get_hotel_non_existing(self):
        """Test pobierania nieistniejącego hotelu"""
        retrieved_hotel = self.db.get_hotel("H1")
        self.assertIsNone(retrieved_hotel)

    def test_search_hotels_by_location(self):
        """Test wyszukiwania hoteli po lokalizacji"""
        self.db.add_hotel(self.hotel1)  # Warszawa
        self.db.add_hotel(self.hotel2)  # Kraków
        self.db.add_hotel(self.hotel3)  # Warszawa

        warsaw_hotels = self.db.search_hotels(location="warszawa")
        self.assertEqual(len(warsaw_hotels), 2)
        self.assertIn(self.hotel1, warsaw_hotels)
        self.assertIn(self.hotel3, warsaw_hotels)

    def test_search_hotels_by_rating(self):
        """Test wyszukiwania hoteli po ocenie"""
        self.db.add_hotel(self.hotel1)  # 4 gwiazdki
        self.db.add_hotel(self.hotel2)  # 5 gwiazdek
        self.db.add_hotel(self.hotel3)  # 3 gwiazdki

        high_rated_hotels = self.db.search_hotels(min_rating=4)
        self.assertEqual(len(high_rated_hotels), 2)
        self.assertIn(self.hotel1, high_rated_hotels)
        self.assertIn(self.hotel2, high_rated_hotels)

    def test_search_hotels_by_location_and_rating(self):
        """Test wyszukiwania hoteli po lokalizacji i ocenie"""
        self.db.add_hotel(self.hotel1)  # Warszawa, 4 gwiazdki
        self.db.add_hotel(self.hotel2)  # Kraków, 5 gwiazdek
        self.db.add_hotel(self.hotel3)  # Warszawa, 3 gwiazdki

        result = self.db.search_hotels(location="warszawa", min_rating=4)
        self.assertEqual(len(result), 1)
        self.assertIn(self.hotel1, result)

    def test_search_hotels_invalid_rating(self):
        """Test wyszukiwania hoteli z nieprawidłową minimalną oceną"""
        invalid_ratings = [0, 6, -1]
        for rating in invalid_ratings:
            with self.subTest(rating=rating):
                with self.assertRaises(ValueError):
                    self.db.search_hotels(min_rating=rating)


if __name__ == '__main__':
    unittest.main()