# data/booking_system.py

import uuid
from dataclasses import dataclass, field
from typing import List, Dict
from datetime import datetime

from data.exceptions import SeatUnavailableError, NotFoundError, ValidationError

# -------------------------
# Models
# -------------------------
@dataclass
class Seat:
    seat_id: str
    row: str
    number: int
    price: float
    is_reserved: bool = False

    def reserve(self):
        if self.is_reserved:
            raise SeatUnavailableError(f"Seat {self.seat_id} is already reserved.")
        self.is_reserved = True

    def release(self):
        self.is_reserved = False

@dataclass
class Event:
    event_id: str
    name: str
    date: str  # ISO date string
    location: str
    seats: List[Seat] = field(default_factory=list)

    def get_available_seats(self):
        return [s for s in self.seats if not s.is_reserved]

    def find_seat(self, seat_id: str) -> Seat:
        for s in self.seats:
            if s.seat_id == seat_id:
                return s
        raise NotFoundError(f"Seat {seat_id} not found in event {self.event_id}.")

@dataclass
class Customer:
    customer_id: str
    name: str
    email: str

@dataclass
class Ticket:
    ticket_id: str
    event_id: str
    seat_id: str
    customer_id: str
    price: float
    created_at: str
    status: str = "booked"  # or "cancelled"

    def cancel(self):
        if self.status == "cancelled":
            raise ValidationError("Ticket already cancelled.")
        self.status = "cancelled"

# -------------------------
# Booking Manager
# -------------------------
class BookingManager:
    def __init__(self):
        self.events: Dict[str, Event] = {}
        self.customers: Dict[str, Customer] = {}
        self.tickets: Dict[str, Ticket] = {}

    # -- create helpers
    def add_event(self, name: str, date: str, location: str, seats: List[Seat]) -> Event:
        eid = str(uuid.uuid4())
        evt = Event(event_id=eid, name=name, date=date, location=location, seats=seats)
        self.events[eid] = evt
        return evt

    def register_customer(self, name: str, email: str) -> Customer:
        cid = str(uuid.uuid4())
        cust = Customer(customer_id=cid, name=name, email=email)
        self.customers[cid] = cust
        return cust

    # -- booking / cancel
    def book_seat(self, event_id: str, seat_id: str, customer_id: str) -> Ticket:
        if event_id not in self.events:
            raise NotFoundError("Event not found.")
        if customer_id not in self.customers:
            raise NotFoundError("Customer not found.")

        event = self.events[event_id]
        seat = event.find_seat(seat_id)   # may raise NotFoundError
        seat.reserve()                    # may raise SeatUnavailableError

        tid = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        ticket = Ticket(ticket_id=tid,
                        event_id=event_id,
                        seat_id=seat_id,
                        customer_id=customer_id,
                        price=seat.price,
                        created_at=created_at)
        self.tickets[tid] = ticket
        return ticket

    def cancel_ticket(self, ticket_id: str):
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            raise NotFoundError("Ticket not found.")
        if ticket.status == "cancelled":
            raise ValidationError("Ticket already cancelled.")

        event = self.events.get(ticket.event_id)
        if event:
            try:
                seat = event.find_seat(ticket.seat_id)
                seat.release()
            except NotFoundError:
                # seat missing in event — ignore seat release but continue cancelling ticket
                pass

        ticket.cancel()

    # -- queries
    def list_events(self) -> List[Event]:
        return list(self.events.values())

    def list_tickets_for_customer(self, customer_id: str) -> List[Ticket]:
        return [t for t in self.tickets.values() if t.customer_id == customer_id]

    # -- helper: seed demo
    def seed_demo(self):
        seats = [
            Seat(seat_id="A1", row="A", number=1, price=50.0),
            Seat(seat_id="A2", row="A", number=2, price=50.0),
            Seat(seat_id="B1", row="B", number=1, price=40.0),
        ]
        evt = self.add_event(name="Demo Concert", date="2025-11-15", location="Grand Hall", seats=seats)
        return evt
