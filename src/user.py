"""
Moduł zarządzający użytkownikami systemu hotelowego.
Zawiera klasy do rejestracji, uwierzytelniania i zarządzania danymi użytkowników.

"""

from typing import Dict, Optional, Any
import re
import hashlib
import uuid


class User:
    """Klasa reprezentująca użytkownika systemu."""

    def __init__(self, user_id: str, first_name: str, last_name: str,
                 email: str, phone: str, password_hash: str):
        """
        Inicjalizuje nowego użytkownika.

        Args:
            user_id: Unikalny identyfikator użytkownika
            first_name: Imię użytkownika
            last_name: Nazwisko użytkownika
            email: Adres email użytkownika
            phone: Numer telefonu użytkownika
            password_hash: Zahashowane hasło użytkownika
        """
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.password_hash = password_hash

    @classmethod
    def create(cls, first_name: str, last_name: str, email: str,
               phone: str, password: str) -> 'User':
        """
        Tworzy nowego użytkownika z podanych danych.

        Args:
            first_name: Imię użytkownika
            last_name: Nazwisko użytkownika
            email: Adres email użytkownika
            phone: Numer telefonu użytkownika
            password: Hasło użytkownika

        Returns:
            Nowy obiekt użytkownika

        Raises:
            ValueError: Gdy dane są niepoprawne
        """
        # Usuwanie białych znaków
        first_name = first_name.strip()
        last_name = last_name.strip()
        email = email.strip()
        phone = phone.strip()

        # Walidacja danych
        if not all([first_name, last_name, email, phone, password]):
            raise ValueError("Wszystkie pola są wymagane")

        # Walidacja imienia i nazwiska (brak cyfr)
        if re.search(r'\d', first_name) or re.search(r'\d', last_name):
            raise ValueError("Imię i nazwisko nie mogą zawierać cyfr")

        # Walidacja długości imienia
        if len(first_name) > 100:
            raise ValueError("Imię nie może być dłuższe niż 100 znaków")

        # Walidacja emaila
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Nieprawidłowy format adresu email")

        # Walidacja numeru telefonu
        phone_pattern = r'^\+?[0-9]{9,15}$'
        if not re.match(phone_pattern, phone):
            raise ValueError("Nieprawidłowy format numeru telefonu")

        # Walidacja hasła
        cls._validate_password(password)

        # Generowanie ID użytkownika
        user_id = str(uuid.uuid4())

        # Hashowanie hasła
        password_hash = cls._hash_password(password)

        return cls(
            user_id=user_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            password_hash=password_hash
        )

    @staticmethod
    def _validate_password(password: str) -> None:
        """
        Waliduje hasło pod kątem długości i złożoności.

        Args:
            password: Hasło do zwalidowania

        Raises:
            ValueError: Gdy hasło nie spełnia wymagań
        """
        if len(password) < 8:
            raise ValueError("Hasło musi mieć co najmniej 8 znaków")

        # Walidacja złożoności hasła (wymagane co najmniej jedna litera i jedna cyfra)
        if not (re.search(r'[a-zA-Z]', password) and re.search(r'\d', password)):
            raise ValueError("Hasło musi zawierać co najmniej jedną literę i jedną cyfrę")

    @staticmethod
    def _hash_password(password: str) -> str:
        """
        Hashuje hasło.

        Args:
            password: Hasło do zahashowania

        Returns:
            Zahashowane hasło
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def verify_password(self, password: str) -> bool:
        """
        Weryfikuje poprawność hasła.

        Args:
            password: Hasło do weryfikacji

        Returns:
            True jeśli hasło jest poprawne, False w przeciwnym przypadku
        """
        return self._hash_password(password) == self.password_hash

    def full_name(self) -> str:
        """
        Zwraca pełne imię i nazwisko.

        Returns:
            Imię i nazwisko połączone spacją
        """
        return f"{self.first_name} {self.last_name}"

    def update_data(self, **kwargs) -> None:
        """
        Aktualizuje dane użytkownika.

        Args:
            **kwargs: Pola do zaktualizowania (first_name, last_name, email, phone)

        Raises:
            ValueError: Gdy dane są niepoprawne
        """
        if 'email' in kwargs:
            email = kwargs['email'].strip()
            # Walidacja emaila
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                raise ValueError("Nieprawidłowy format adresu email")
            self.email = email

        if 'first_name' in kwargs:
            first_name = kwargs['first_name'].strip()
            if not first_name:
                raise ValueError("Imię nie może być puste")
            if re.search(r'\d', first_name):
                raise ValueError("Imię nie może zawierać cyfr")
            if len(first_name) > 100:
                raise ValueError("Imię nie może być dłuższe niż 100 znaków")
            self.first_name = first_name

        if 'last_name' in kwargs:
            last_name = kwargs['last_name'].strip()
            if not last_name:
                raise ValueError("Nazwisko nie może być puste")
            if re.search(r'\d', last_name):
                raise ValueError("Nazwisko nie może zawierać cyfr")
            self.last_name = last_name

        if 'phone' in kwargs:
            phone = kwargs['phone'].strip()
            # Walidacja numeru telefonu
            phone_pattern = r'^\+?[0-9]{9,15}$'
            if not re.match(phone_pattern, phone):
                raise ValueError("Nieprawidłowy format numeru telefonu")
            self.phone = phone

    def change_password(self, old_password: str, new_password: str) -> None:
        """
        Zmienia hasło użytkownika.

        Args:
            old_password: Stare hasło
            new_password: Nowe hasło

        Raises:
            ValueError: Gdy stare hasło jest niepoprawne lub nowe hasło nie spełnia wymagań
        """
        if not self.verify_password(old_password):
            raise ValueError("Niepoprawne hasło")

        # Walidacja nowego hasła
        self._validate_password(new_password)

        self.password_hash = self._hash_password(new_password)

    def to_dict(self, include_password: bool = False) -> Dict[str, Any]:
        """
        Konwertuje obiekt użytkownika do słownika.

        Args:
            include_password: Czy uwzględnić zahashowane hasło

        Returns:
            Słownik z danymi użytkownika
        """
        result = {
            'user_id': self.user_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'phone': self.phone
        }

        if include_password:
            result['password_hash'] = self.password_hash

        return result


class UserManager:
    """Klasa zarządzająca użytkownikami systemu."""

    def __init__(self):
        """Inicjalizuje nowy menedżer użytkowników."""
        self.users: Dict[str, User] = {}
        self.email_to_id: Dict[str, str] = {}

    def register_user(self, first_name: str, last_name: str,
                      email: str, phone: str, password: str) -> User:
        """
        Rejestruje nowego użytkownika.

        Args:
            first_name: Imię użytkownika
            last_name: Nazwisko użytkownika
            email: Adres email użytkownika
            phone: Numer telefonu użytkownika
            password: Hasło użytkownika

        Returns:
            Nowy obiekt użytkownika

        Raises:
            ValueError: Gdy użytkownik o danym emailu już istnieje lub dane są niepoprawne
        """
        # Usunięcie białych znaków z emaila przed sprawdzeniem
        email = email.strip()

        if email in self.email_to_id:
            raise ValueError(f"Użytkownik o emailu {email} już istnieje")

        # Tworzenie użytkownika może rzucić wyjątek, który zostanie propagowany dalej
        user = User.create(first_name, last_name, email, phone, password)

        self.users[user.user_id] = user
        self.email_to_id[email] = user.user_id

        return user

    def get_user(self, user_id: str) -> Optional[User]:
        """
        Zwraca użytkownika o danym ID lub None.

        Args:
            user_id: Identyfikator użytkownika

        Returns:
            Obiekt użytkownika lub None, jeśli nie znaleziono
        """
        return self.users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Zwraca użytkownika o danym emailu lub None.

        Args:
            email: Adres email użytkownika

        Returns:
            Obiekt użytkownika lub None, jeśli nie znaleziono
        """
        # Usunięcie białych znaków z emaila przed wyszukiwaniem
        email = email.strip()

        user_id = self.email_to_id.get(email)
        if user_id:
            return self.users.get(user_id)
        return None

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Uwierzytelnia użytkownika na podstawie emaila i hasła.

        Args:
            email: Adres email użytkownika
            password: Hasło użytkownika

        Returns:
            Obiekt użytkownika jeśli uwierzytelnienie powiodło się, None w przeciwnym przypadku
        """
        # Usunięcie białych znaków z emaila przed uwierzytelnianiem
        email = email.strip()

        user = self.get_user_by_email(email)
        if user and user.verify_password(password):
            return user
        return None
