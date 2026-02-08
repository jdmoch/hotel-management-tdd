"""
Testy jednostkowe dla modułu user.
Testuje klasy User i UserManager odpowiedzialne za zarządzanie danymi użytkowników,
rejestrację, uwierzytelnianie oraz aktualizację informacji o użytkownikach.
"""

import hashlib
import unittest
import uuid

from src.user import User, UserManager


class TestUser(unittest.TestCase):
    """Testy dla klasy User"""

    def test_user_initialization(self):
        """Test poprawnej inicjalizacji użytkownika"""
        user = User("U1", "Jan", "Kowalski", "jan@example.com", "+48123456789", "hashed_password")
        self.assertEqual(user.user_id, "U1")
        self.assertEqual(user.first_name, "Jan")
        self.assertEqual(user.last_name, "Kowalski")
        self.assertEqual(user.email, "jan@example.com")
        self.assertEqual(user.phone, "+48123456789")
        self.assertEqual(user.password_hash, "hashed_password")

    def test_create_user_success(self):
        """Test tworzenia użytkownika z poprawnymi danymi"""
        user = User.create("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")
        self.assertIsInstance(user, User)
        self.assertIsNotNone(user.user_id)
        self.assertEqual(user.first_name, "Jan")
        self.assertEqual(user.last_name, "Kowalski")
        self.assertEqual(user.email, "jan@example.com")
        self.assertEqual(user.phone, "+48123456789")
        self.assertIsNotNone(user.password_hash)

    def test_create_user_missing_fields(self):
        """Test tworzenia użytkownika z brakującymi polami"""
        with self.assertRaises(ValueError):
            User.create("", "Kowalski", "jan@example.com", "+48123456789", "password123")

        with self.assertRaises(ValueError):
            User.create("Jan", "", "jan@example.com", "+48123456789", "password123")

        with self.assertRaises(ValueError):
            User.create("Jan", "Kowalski", "", "+48123456789", "password123")

        with self.assertRaises(ValueError):
            User.create("Jan", "Kowalski", "jan@example.com", "", "password123")

        with self.assertRaises(ValueError):
            User.create("Jan", "Kowalski", "jan@example.com", "+48123456789", "")

    def test_create_user_invalid_email(self):
        """Test tworzenia użytkownika z nieprawidłowym adresem email"""
        invalid_emails = [
            "janexample.com",  # brak @
            "jan@.com",  # brak domeny
            "jan@com",  # niepełna domena
            "@example.com",  # brak nazwy użytkownika
            "jan@example.",  # niepełne rozszerzenie
            "invalid@",
            "invalid@domain",
            "invalid.com",
            "invalid@.com",
            "invalid@domain."
        ]

        for email in invalid_emails:
            with self.assertRaises(ValueError):
                User.create("Jan", "Kowalski", email, "+48123456789", "password123")

    def test_create_user_invalid_phone(self):
        """Test tworzenia użytkownika z nieprawidłowym numerem telefonu"""
        invalid_phones = [
            "123456",  # za krótki
            "abcdefghij",  # zawiera litery
            "+48-123-456-789",  # zawiera myślniki
            "123456789012345678",  # za długi
            "+12345",
            "+12-345-67890",
            "12345678901234567890"
        ]

        for phone in invalid_phones:
            with self.assertRaises(ValueError):
                User.create("Jan", "Kowalski", "jan@example.com", phone, "password123")

    def test_valid_email_formats(self):
        """Test tworzenia użytkownika z różnymi prawidłowymi formatami emaili"""
        valid_emails = [
            "valid@example.com",
            "user.name@domain.com",
            "user+tag@example.co.uk",
            "123456@domain.com",
            "name-with-dash@example.com"
        ]

        for email in valid_emails:
            user = User.create("Jan", "Kowalski", email, "+48123456789", "password123")
            self.assertEqual(user.email, email)

    def test_valid_phone_formats(self):
        """Test tworzenia użytkownika z różnymi prawidłowymi formatami numerów telefonu"""
        valid_phones = [
            "+48123456789",
            "123456789",
            "+1234567890123",
            "0048123456789"
        ]

        for phone in valid_phones:
            user = User.create("Jan", "Kowalski", "jan@example.com", phone, "password123")
            self.assertEqual(user.phone, phone)

    def test_verify_password_correct(self):
        """Test weryfikacji poprawnego hasła"""
        user = User.create("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")
        self.assertTrue(user.verify_password("password123"))

    def test_verify_password_incorrect(self):
        """Test weryfikacji niepoprawnego hasła"""
        user = User.create("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")
        self.assertFalse(user.verify_password("wrongpassword"))

    def test_hash_password(self):
        """Test hashowania hasła"""
        password = "password123"
        expected_hash = hashlib.sha256(password.encode()).hexdigest()
        self.assertEqual(User._hash_password(password), expected_hash)

    def test_full_name(self):
        """Test zwracania pełnego imienia i nazwiska"""
        user = User("U1", "Jan", "Kowalski", "jan@example.com", "+48123456789", "hashed_password")
        self.assertEqual(user.full_name(), "Jan Kowalski")

    def test_create_user_with_whitespace_in_fields(self):
        """Test tworzenia użytkownika z białymi znakami w polach"""
        user = User.create(" Jan ", " Kowalski ", " jan@example.com ", " +48123456789 ", " password123 ")
        # Sprawdzamy czy białe znaki zostały usunięte
        self.assertEqual(user.first_name, "Jan")
        self.assertEqual(user.last_name, "Kowalski")
        self.assertEqual(user.email, "jan@example.com")
        self.assertEqual(user.phone, "+48123456789")
        # Hasło nie powinno mieć usuniętych białych znaków
        self.assertTrue(user.verify_password(" password123 "))

    def test_create_user_with_special_characters_in_name(self):
        """Test tworzenia użytkownika ze specjalnymi znakami w imieniu i nazwisku"""
        user = User.create("Józef", "Łoś-Wąż", "jozef@example.com", "+48123456789", "password123")
        self.assertEqual(user.first_name, "Józef")
        self.assertEqual(user.last_name, "Łoś-Wąż")
        self.assertEqual(user.full_name(), "Józef Łoś-Wąż")

    def test_verify_password_case_sensitive(self):
        """Test weryfikacji hasła z uwzględnieniem wielkości liter"""
        user = User.create("Jan", "Kowalski", "jan@example.com", "+48123456789", "Password123")
        self.assertTrue(user.verify_password("Password123"))
        self.assertFalse(user.verify_password("password123"))

    def test_first_name_with_special_chars_validation(self):
        """Test tworzenia użytkownika ze znakami specjalnymi w imieniu"""
        user = User.create("Jan-Paweł", "Kowalski", "jan@example.com", "+48123456789", "password123")
        self.assertEqual(user.first_name, "Jan-Paweł")

    def test_user_dictionary_with_password(self):
        """Test konwersji obiektu User do słownika z hasłem"""
        user = User("U1", "Jan", "Kowalski", "jan@example.com", "+48123456789", "hashed_password")
        user_dict = user.to_dict(include_password=True)
        self.assertIn("password_hash", user_dict)
        self.assertEqual(user_dict["password_hash"], "hashed_password")

    def test_update_multiple_fields(self):
        """Test aktualizacji wielu pól użytkownika jednocześnie"""
        user = User("U1", "Jan", "Kowalski", "jan@example.com", "+48123456789", "hashed_password")
        user.update_data(first_name="Janusz", last_name="Nowak", email="janusz@example.com", phone="+48987654321")
        self.assertEqual(user.first_name, "Janusz")
        self.assertEqual(user.last_name, "Nowak")
        self.assertEqual(user.email, "janusz@example.com")
        self.assertEqual(user.phone, "+48987654321")

    def test_update_empty_fields(self):
        """Test aktualizacji pól użytkownika pustymi wartościami"""
        user = User("U1", "Jan", "Kowalski", "jan@example.com", "+48123456789", "hashed_password")
        with self.assertRaises(ValueError):
            user.update_data(first_name="")
        with self.assertRaises(ValueError):
            user.update_data(last_name="")

    def test_change_password_complexity_validation(self):
        """Test zmiany hasła z walidacją złożoności nowego hasła"""
        user = User.create("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")
        with self.assertRaises(ValueError):
            user.change_password("password123", "onlyletters")
        with self.assertRaises(ValueError):
            user.change_password("password123", "12345678")
        with self.assertRaises(ValueError):
            user.change_password("password123", "short1")


class TestUserManager(unittest.TestCase):
    """Testy dla klasy UserManager"""

    def setUp(self):
        """Przygotowanie środowiska testowego przed każdym testem"""
        self.manager = UserManager()

    def test_register_user_success(self):
        """Test rejestracji nowego użytkownika z powodzeniem"""
        user = self.manager.register_user("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, "jan@example.com")
        self.assertIn(user.user_id, self.manager.users)
        self.assertEqual(self.manager.email_to_id["jan@example.com"], user.user_id)

    def test_register_user_duplicate_email(self):
        """Test rejestracji użytkownika z istniejącym emailem"""
        self.manager.register_user("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")

        with self.assertRaises(ValueError):
            self.manager.register_user("Anna", "Nowak", "jan@example.com", "+48987654321", "password456")

    def test_get_user_existing(self):
        """Test pobierania istniejącego użytkownika po ID"""
        user = self.manager.register_user("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")
        retrieved_user = self.manager.get_user(user.user_id)
        self.assertEqual(retrieved_user, user)

    def test_get_user_non_existing(self):
        """Test pobierania nieistniejącego użytkownika po ID"""
        non_existing_id = str(uuid.uuid4())
        retrieved_user = self.manager.get_user(non_existing_id)
        self.assertIsNone(retrieved_user)

    def test_get_user_by_email_existing(self):
        """Test pobierania istniejącego użytkownika po emailu"""
        user = self.manager.register_user("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")
        retrieved_user = self.manager.get_user_by_email("jan@example.com")
        self.assertEqual(retrieved_user, user)

    def test_get_user_by_email_non_existing(self):
        """Test pobierania nieistniejącego użytkownika po emailu"""
        retrieved_user = self.manager.get_user_by_email("nonexistent@example.com")
        self.assertIsNone(retrieved_user)

    def test_authenticate_valid_credentials(self):
        """Test uwierzytelniania z prawidłowymi danymi"""
        user = self.manager.register_user("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")
        authenticated_user = self.manager.authenticate("jan@example.com", "password123")
        self.assertEqual(authenticated_user, user)

    def test_authenticate_invalid_email(self):
        """Test uwierzytelniania z nieprawidłowym emailem"""
        self.manager.register_user("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")
        authenticated_user = self.manager.authenticate("nonexistent@example.com", "password123")
        self.assertIsNone(authenticated_user)

    def test_authenticate_invalid_password(self):
        """Test uwierzytelniania z nieprawidłowym hasłem"""
        self.manager.register_user("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")
        authenticated_user = self.manager.authenticate("jan@example.com", "wrongpassword")
        self.assertIsNone(authenticated_user)

    def test_register_multiple_users(self):
        """Test rejestracji wielu użytkowników"""
        user1 = self.manager.register_user("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")
        user2 = self.manager.register_user("Anna", "Nowak", "anna@example.com", "+48987654321", "password456")

        self.assertEqual(len(self.manager.users), 2)
        self.assertEqual(self.manager.get_user(user1.user_id), user1)
        self.assertEqual(self.manager.get_user(user2.user_id), user2)
        self.assertEqual(self.manager.get_user_by_email("jan@example.com"), user1)
        self.assertEqual(self.manager.get_user_by_email("anna@example.com"), user2)

    def test_authenticate_with_whitespace_in_email(self):
        """Test uwierzytelniania z białymi znakami w emailu"""
        self.manager.register_user("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")
        authenticated_user = self.manager.authenticate(" jan@example.com ", "password123")
        self.assertIsNotNone(authenticated_user)
        self.assertEqual(authenticated_user.email, "jan@example.com")

    def test_password_too_short(self):
        """Test tworzenia użytkownika ze zbyt krótkim hasłem"""
        with self.assertRaises(ValueError):
            User.create("Jan", "Kowalski", "jan@example.com", "+48123456789", "abc")

    def test_password_complexity(self):
        """Test tworzenia użytkownika z hasłem niespełniającym wymogów złożoności"""
        with self.assertRaises(ValueError):
            User.create("Jan", "Kowalski", "jan@example.com", "+48123456789", "12345678")

    def test_update_user_data(self):
        """Test aktualizacji danych użytkownika"""
        user = User("U1", "Jan", "Kowalski", "jan@example.com", "+48123456789", "hashed_password")
        user.update_data(first_name="Janusz", email="janusz@example.com")
        self.assertEqual(user.first_name, "Janusz")
        self.assertEqual(user.email, "janusz@example.com")
        self.assertEqual(user.last_name, "Kowalski")

    def test_update_user_invalid_email(self):
        """Test aktualizacji danych użytkownika z nieprawidłowym emailem"""
        user = User("U1", "Jan", "Kowalski", "jan@example.com", "+48123456789", "hashed_password")
        with self.assertRaises(ValueError):
            user.update_data(email="invalid-email")

    def test_update_user_invalid_email_format(self):
        """Test aktualizacji emaila na nieprawidłowy format"""
        user = User.create("Jan", "Kowalski", "jan@example.com", "+48123456789", "Password123!")

        with self.assertRaises(ValueError):
            user.update_data(email="niepoprawny_email")

    def test_to_dict(self):
        """Test konwersji obiektu User do słownika"""
        user = User("U1", "Jan", "Kowalski", "jan@example.com", "+48123456789", "hashed_password")
        user_dict = user.to_dict(include_password=False)
        self.assertEqual(user_dict["user_id"], "U1")
        self.assertEqual(user_dict["first_name"], "Jan")
        self.assertEqual(user_dict["last_name"], "Kowalski")
        self.assertEqual(user_dict["email"], "jan@example.com")
        self.assertEqual(user_dict["phone"], "+48123456789")
        self.assertNotIn("password_hash", user_dict)

    def test_name_with_numbers(self):
        """Test tworzenia użytkownika z liczbami w imieniu i nazwisku"""
        with self.assertRaises(ValueError):
            User.create("Jan123", "Kowalski", "jan@example.com", "+48123456789", "password123")

    def test_email_with_unicode(self):
        """Test tworzenia użytkownika z emailem zawierającym znaki Unicode"""
        with self.assertRaises(ValueError):
            User.create("Jan", "Kowalski", "jań@example.com", "+48123456789", "password123")

    def test_change_password(self):
        """Test zmiany hasła użytkownika"""
        user = User.create("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")
        old_hash = user.password_hash
        user.change_password("password123", "newPassword456")
        self.assertNotEqual(user.password_hash, old_hash)
        self.assertTrue(user.verify_password("newPassword456"))
        self.assertFalse(user.verify_password("password123"))

    def test_change_password_invalid_old_password(self):
        """Test zmiany hasła z niepoprawnym starym hasłem"""
        user = User.create("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")
        old_hash = user.password_hash
        with self.assertRaises(ValueError):
            user.change_password("wrongPassword", "newPassword456")
        self.assertEqual(user.password_hash, old_hash)

    def test_first_name_too_long(self):
        """Test tworzenia użytkownika ze zbyt długim imieniem"""
        with self.assertRaises(ValueError):
            User.create("J" * 101, "Kowalski", "jan@example.com", "+48123456789", "password123")

    def test_register_with_whitespace_in_fields(self):
        """Test rejestracji użytkownika z białymi znakami w polach"""
        user = self.manager.register_user(" Jan ", " Kowalski ", " jan@example.com ", " +48123456789 ", " password123 ")
        self.assertEqual(user.first_name, "Jan")
        self.assertEqual(user.last_name, "Kowalski")
        self.assertEqual(user.email, "jan@example.com")
        self.assertEqual(user.phone, "+48123456789")

    def test_case_insensitive_email_authentication(self):
        """Test uwierzytelniania z różnymi wersjami wielkości liter w emailu"""
        self.manager.register_user("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")
        authenticated_user = self.manager.authenticate("JAN@example.com", "password123")
        self.assertIsNone(authenticated_user)

    def test_get_user_by_email_with_whitespace(self):
        """Test pobierania użytkownika po emailu z białymi znakami"""
        user = self.manager.register_user("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")
        retrieved_user = self.manager.get_user_by_email(" jan@example.com ")
        self.assertEqual(retrieved_user, user)

    def test_register_user_with_invalid_data(self):
        """Test rejestracji użytkownika z nieprawidłowymi danymi"""
        with self.assertRaises(ValueError):
            self.manager.register_user("Jan123", "Kowalski", "jan@example.com", "+48123456789", "password123")

    def test_register_user_with_invalid_phone_after_stripping(self):
        """Test rejestracji z numerem telefonu zawierającym nieprawidłowe znaki"""
        manager = UserManager()

        with self.assertRaises(ValueError):
            manager.register_user(
                first_name="Anna",
                last_name="Nowak",
                email="anna@example.com",
                phone="+48-123-456-789",
                password="Password123!"
            )

    def test_user_id_uniqueness(self):
        """Test unikalności ID użytkowników"""
        user1 = self.manager.register_user("Jan", "Kowalski", "jan@example.com", "+48123456789", "password123")
        user2 = self.manager.register_user("Anna", "Nowak", "anna@example.com", "+48987654321", "password456")
        self.assertNotEqual(user1.user_id, user2.user_id)

if __name__ == '__main__':
    unittest.main()