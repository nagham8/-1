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
            # --- создать событие ---
            try:
                name = input("Название события: ").strip()
                date = input("Дата события (YYYY-MM-DD): ").strip()
                location = input("Место проведения: ").strip()
                num_seats = int(input("Количество мест: ").strip())
                seats = []
                for i in range(num_seats):
                    row = input(f"Ряд для места {i + 1}: ").strip().upper()
                    number = int(input(f"Номер места {i + 1}: ").strip())
                    price = float(input(f"Цена места {i + 1}: ").strip())
                    seat_id = f"{row}{number}"
                    seats.append(Seat(seat_id=seat_id, row=row, number=number, price=price))
                event = manager.add_event(name, date, location, seats)
                print(f"Событие создано: {event.event_id} - {event.name}")
            except Exception as e:
                print("Ошибка при создании события:", e)
            input("Нажмите Enter, чтобы продолжить...")

        elif choice == "2":
            # --- зарегистрировать клиента ---
            try:
                name = input("Имя клиента: ").strip()
                email = input("Email клиента: ").strip()
                customer = manager.register_customer(name, email)
                print(f"Клиент зарегистрирован: {customer.customer_id} - {customer.name}")
            except Exception as e:
                print("Ошибка при регистрации клиента:", e)
            input("Нажмите Enter, чтобы продолжить...")

        elif choice == "3":
            # --- показать все события ---
            events = manager.list_events()
            if not events:
                print("События отсутствуют.")
            else:
                for e in events:
                    print(
                        f"{e.event_id} - {e.name} ({e.date}) в {e.location}, доступных мест: {len(e.get_available_seats())}")
            input("Нажмите Enter, чтобы продолжить...")

        elif choice == "4":
            # --- забронировать билет ---
            try:
                event_id = input("ID события: ").strip()
                customer_id = input("ID клиента: ").strip()
                seat_id = input("ID места: ").strip()
                ticket = manager.book_seat(event_id, seat_id, customer_id)
                print(f"Билет забронирован: {ticket.ticket_id}, место: {ticket.seat_id}")
            except BookingError as e:
                print("Ошибка бронирования:", e)
            except Exception as e:
                print("Неизвестная ошибка:", e)
            input("Нажмите Enter, чтобы продолжить...")

        elif choice == "5":
            # --- отменить бронь ---
            try:
                ticket_id = input("ID билета: ").strip()
                manager.cancel_ticket(ticket_id)
                print(f"Бронь билета {ticket_id} отменена.")
            except BookingError as e:
                print("Ошибка отмены:", e)
            except Exception as e:
                print("Неизвестная ошибка:", e)
            input("Нажмите Enter, чтобы продолжить...")

        elif choice == "6":
            # --- показать доступные места для события ---
            try:
                event_id = input("ID события: ").strip()
                event = manager.events.get(event_id)
                if not event:
                    print("Событие не найдено.")
                else:
                    seats = event.get_available_seats()
                    if not seats:
                        print("Доступных мест нет.")
                    for s in seats:
                        print(
                            f"Место {s.seat_id} - ряд {s.row} номер {s.number} - цена {s.price} - {'занято' if s.is_reserved else 'свободно'}")
            except Exception as e:
                print("Ошибка:", e)
            input("Нажмите Enter, чтобы продолжить...")

        elif choice == "7":
            # --- сохранить данные ---
            try:
                storage.save_to_json(manager)
                storage.save_to_xml(manager)
                print("Данные успешно сохранены в JSON и XML.")
            except Exception as e:
                print("Ошибка при сохранении данных:", e)
            input("Нажмите Enter, чтобы продолжить...")

        elif choice == "8":
            # --- загрузить данные ---
            try:
                storage.load_from_json(manager)
                storage.load_from_xml(manager)
                print("Данные успешно загружены из JSON и XML.")
            except Exception as e:
                print("Ошибка при загрузке данных:", e)
            input("Нажмите Enter, чтобы продолжить...")

        elif choice == "0":
            print("Выход из программы...")
            break

        else:
            print("Некорректный выбор. Попробуйте снова.")
            input("Нажмите Enter, чтобы продолжить...")
