# Przypadki użycia w scenariuszach zderzone z modelem danych


## Użytkownik
Korzystamy z integracji z google 
- Użytkownik loguje się kontem googla. 
- Tworzymy wpis w tabeli Users dodając email i user_name otrzymany z SSO Google. 
- user_id nadawane jest automatycznie i stanowi punkt wyjścia dla dalszej struktury.

## Tworzenie householda
- Użytkownik jest zalogowany, przechowujemy jego user_id.
- Użytkownik wpisuje nazwę householda.
- Dodajemy rekord w tabeli households, pobieramy hous_id.
- Dodajemy rekord w tabeli household_members (hous_id,user_id).

## Oglądanie householdów.
- Użytkownik jest zalogowany.
- Użytkownik wybiera pokaż moje householdy.
- Wykonujemy złączenie users po user_id z household_members po hsme_hous_id z households.
- Wybieramy potrzebne pola i pokazujemy liste.

## Oglądanie i modyfikowanie householda.
 - Użytkownik wybrał household (mamy hous_id)
 - Wybieramy household z tabeli households.
 - Wyświetlamy lub modyfikujemy.

## Oglądanie członków gospodarstwa.
 - Użytkownik wybrał household i prosi o członków.
 - Odpytujemy tabele household_members po hsme_hous_id i łączymy po hsme_user_id z users.
 - Wybieramy potrzebne kulumny i wyświetlamy.

## Dodawanie członka.
 - Zalogowany użytkownik podaje email członka którego chce dodać.
 - Pobieramy id z tabli users wyszukując po email.
 - Jeśli istnieje dodajemy rekord w tabeli household_members (hous_id,user_id).
 - Jeśli nie istnieje wysyłamy że nie znamy i sugerujemy wysłanie prośby o założenie konta.

## Oglądanie harmonogram obowiązków
 - Mamy wybrany household.
 - Odpytujemy table chores po chor_hous_id.
 - Wybieramy potrzebne kolumny i wyświetlamy.

## Dodanie zadania
 - Mamy wybrany household.
 - Użytkownik wybiera opcje dodaj zadanie.
 - Pobiermy z bazki list imion członków household'a: odpytujemy tabele household_members po hsme_hous_id i łączymy po hsme_user_id z users.
 - Użytkownik wprawadza dane oraz wybiera imie przypisanego członka.
 - Dodajemy wpis w chores 
