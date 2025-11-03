# ui/menu.py

import os
from data.booking_system import BookingManager, Seat
from data import storage
from data.exceptions import BookingError

# -------------------------
# Функция для очистки консоли
# -------------------------
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


# -------------------------
# Функция для красивого отображения таблицы мест
# -------------------------
def print_seat_table(seats):
    print("\nДоступные места:\n")
    print(f"{'ID места':<10} | {'Ряд':<5} | {'Номер':<6} | {'Цена ($)':<10} | {'Статус':<10}")
    print("-" * 50)
    for s in seats:
        status = "❌ Занято" if s.is_reserved else "✅ Свободно"
        print(f"{s.seat_id:<10} | {s.row:<5} | {s.number:<6} | {s.price:<10.2f} | {status:<10}")
    print("-" * 50)


# -------------------------
# Главная функция меню
# -------------------------
def run_menu():
    manager = BookingManager()  # создаем менеджер бронирования
    while True:
        clear_screen()
        print("--- Система бронирования билетов ---")
        print("1. Создать новое событие")
        print("2. Зарегистрировать клиента")
        print("3. Показать все события")
        print("4. Забронировать билет")
        print("5. Отменить бронь")
        print("6. Показать доступные места")
        print("7. Сохранить данные")
        print("8. Загрузить данные")
        print("0. Выход")

        choice = input("Выберите действие: ").strip()

        if choice == "1":
            try:
                name = input("Название события: ").strip()
                date = input("Дата события (YYYY-MM-DD): ").strip()
                location = input("Место проведения: ").strip()
                num_seats = int(input("Количество мест: ").strip())
                seats = []
                for i in range(num_seats):
                    row = input(f"Ряд для места {i + 1}: ").strip().upper()
                    number = int(input(f"Номер места {i + 1}: ").strip())
                    price = float(input(f"Цена места {i + 1} ($): ").strip())
                    seat_id = f"{row}{number}"
                    seats.append(Seat(seat_id=seat_id, row=row, number=number, price=price))
                event = manager.add_event(name, date, location, seats)
                print(f"\nСобытие создано: {event.event_id} - {event.name}")
            except Exception as e:
                print("Ошибка при создании события:", e)
            input("\nНажмите Enter, чтобы продолжить...")

        elif choice == "2":
            try:
                name = input("Имя клиента: ").strip()
                email = input("Email клиента: ").strip()
                customer = manager.register_customer(name, email)
                print(f"\nКлиент зарегистрирован: {customer.customer_id} - {customer.name}")
            except Exception as e:
                print("Ошибка при регистрации клиента:", e)
            input("\nНажмите Enter, чтобы продолжить...")

        elif choice == "3":
            events = manager.list_events()
            if not events:
                print("События отсутствуют.")
            else:
                for e in events:
                    print(
                        f"{e.event_id} - {e.name} ({e.date}) в {e.location}, доступных мест: {len(e.get_available_seats())}"
                    )
            input("\nНажмите Enter, чтобы продолжить...")

        elif choice == "4":
            try:
                event_id = input("ID события: ").strip()
                event = manager.events.get(event_id)
                if not event:
                    print("Событие не найдено.")
                else:
                    available = event.get_available_seats()
                    if not available:
                        print("Нет доступных мест.")
                    else:
                        print_seat_table(available)
                        seat_id = input("\nВведите ID места, которое хотите забронировать: ").strip()
                        customer_id = input("Введите ID клиента: ").strip()
                        ticket = manager.book_seat(event_id, seat_id, customer_id)
                        print(f"\nБилет забронирован: {ticket.ticket_id}, место: {ticket.seat_id}")
            except BookingError as e:
                print("Ошибка бронирования:", e)
            except Exception as e:
                print("Неизвестная ошибка:", e)
            input("\nНажмите Enter, чтобы продолжить...")

        elif choice == "5":
            try:
                ticket_id = input("ID билета: ").strip()
                manager.cancel_ticket(ticket_id)
                print(f"Бронь билета {ticket_id} отменена.")
            except BookingError as e:
                print("Ошибка отмены:", e)
            except Exception as e:
                print("Неизвестная ошибка:", e)
            input("\nНажмите Enter, чтобы продолжить...")

        elif choice == "6":
            try:
                event_id = input("ID события: ").strip()
                event = manager.events.get(event_id)
                if not event:
                    print("Событие не найдено.")
                else:
                    print_seat_table(event.seats)
            except Exception as e:
                print("Ошибка:", e)
            input("\nНажмите Enter, чтобы продолжить...")

        elif choice == "7":
            try:
                storage.save_to_json(manager)
                storage.save_to_xml(manager)
                print("Данные успешно сохранены в JSON и XML.")
            except Exception as e:
                print("Ошибка при сохранении данных:", e)
            input("\nНажмите Enter, чтобы продолжить...")

        elif choice == "8":
            try:
                storage.load_from_json(manager)
                storage.load_from_xml(manager)
                print("Данные успешно загружены из JSON и XML.")
            except Exception as e:
                print("Ошибка при загрузке данных:", e)
            input("\nНажмите Enter, чтобы продолжить...")

        elif choice == "0":
            print("Выход из программы...")
            break

        else:
            print("Некорректный выбор. Попробуйте снова.")
            input("\nНажмите Enter, чтобы продолжить...")
