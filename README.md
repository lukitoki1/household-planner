# Household Planner
#### Dokumentacja oraz sprawozdanie projektu z przedmiotu "Programowanie usług w chmurze"

Łukasz Kamiński,
Mateusz Kossakowski,
Arkadiusz Mochalak,
Rafał Pachnia,
Ernest Szypuła.

## Wstęp

W ramach projektu zdecydowano się na realizację aplikacji umożliwiającej zarządzanie obowiązkami
gospodarstwa domowego. Aplikację nazwano "Household Planner". Aby pokazać potencjał chmury 
obliczeniowej, funkcjonalność aplikacji zrealizowano w całości w oparciu o usługi dostępne
w Google Cloud Platform (GCP).

## Przypadki użycia

Aplikacja "Household Planner" służy do zarządzania obowiązakmi domowymi w gospodarstwie użytkownika.
Do logowania oraz rejestracji wykorztywane jest Konto Google.

![Diagram przypadkow uzycia 1-2](./doc/final/use_case_1_2.png)

Pierwszym ekranem widocznym po zalogowaniu jest lista gospodarstw domowych, kto których 
użytkoenik należy. Z opziomu listy można przejść do szczegółów gospodarstwa lub utworzyć nowe 
gospodarstwo domowe. 

W aplikacji istnieje również możliwość edycji danych kontaktowych użytkownika.

Z poziomu szczegółów gospodarstwa domowego istnieje możliwość edycji gospodarstwa, wyświetlenia 
członków gospodarstwa oraz wyświetlenie harmonogramu (listy) obowiązków domowych.

![Diagram przypadkow uzycia 3-4](./doc/final/use_case_3_4.png)

Harmonogram obowiązków domowych pozwala na filtrowanie obowiązków, dodanie nowego obowiązku oraz 
oferuje możliwość przejścia do szczegółów obowiązku domowego.

Lista członków gospodarstwa domowego pozwala na ich wyświetlenie oraz edycję: dodanie i usunięcie.

![Diagram przypadkow uzycia 5-6](./doc/final/use_case_5_6.png)

Szczegóły obowiązku domowego zawierają takie informacje, jak: opis obowiązku oraz osoba przypisana
do wykonywania obowiązku. Opis obowiązku można przetłumaczyć na jeden z oferowanych języków,
zaś wykonawcę obowiązku można przydzielić spośród członków gospodarstwa domowego. Istnieje również
możliwość edycji obowiązku (np. jego harmonogramu).

Każdy obowiązek domowy posiada album zdjęć. Zdjęcia można wyświetlić, dodać oraz usunąć.

## Architektura i wykorzystane technologie

![Diagram architektury](./doc/final/architecture.png)

aaa

## Sposób realizacji

aa

## Zaimplementowana funkcjonalność

screeny z apki

## Wyzwania

Zabezpieczenie endpointów:

* globalne zabezpieczenie tokenem autoryzacyjnym
* nie można przypisać kogoś spoza gospodarstwa
* ktoś spoza gospodarstwa nie może korzystać z endpointów gospodarstwa
* zabezpieczenie przed householdami, których nikt nie widzi,
* usuwanie przypisania do chore'ów gdy usuwamy użytkownika z householdu,
* usuwanie zdjęć gdy usuwamy chore
* usuwanie chore'ów oraz asocjacji użytkoeników, gdy usuwamy household.

## Wnioski

aa

## Repozytoria

Projekt był realizowany w repozytoriach dedykowanych przechowywaniu określonych komponentów 
projektu:

* https://github.com/lukitoki1/household-planner - Back-End aplikacji
* https://github.com/lukitoki1/household-planner-frontend - Front-End aplikacji
* https://github.com/ErnestSzypula/household-planner-terraform - Terraform infrastruktury aplikacji

