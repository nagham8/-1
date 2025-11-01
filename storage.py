# data/storage.py

import json
import xml.etree.ElementTree as ET
from typing import Any
from data.booking_system import Event, Seat, Customer, Ticket, BookingManager

# -------------------------
# JSON
# -------------------------
def save_to_json(manager: BookingManager, filename: str = "data.json"):
    data = {
        "events": [
            {
                "event_id": e.event_id,
                "name": e.name,
                "date": e.date,
                "location": e.location,
                "seats": [
                    {
                        "seat_id": s.seat_id,
                        "row": s.row,
                        "number": s.number,
                        "price": s.price,
                        "is_reserved": s.is_reserved
                    } for s in e.seats
                ]
            } for e in manager.events.values()
        ],
        "customers": [
            {"customer_id": c.customer_id, "name": c.name, "email": c.email}
            for c in manager.customers.values()
        ],
        "tickets": [
            {
                "ticket_id": t.ticket_id,
                "event_id": t.event_id,
                "seat_id": t.seat_id,
                "customer_id": t.customer_id,
                "price": t.price,
                "created_at": t.created_at,
                "status": t.status

            } for t in manager.tickets.values()
        ]
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_from_json(manager: BookingManager, filename: str = "data.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"JSON file '{filename}' not found.")
    except Exception as e:
        raise RuntimeError(f"Error reading JSON: {e}")

    # clear current
    manager.events.clear()
    manager.customers.clear()
    manager.tickets.clear()

    # load events
    for e in data.get("events", []):
        seats = [Seat(s["seat_id"], s["row"], int(s["number"]), float(s["price"]), bool(s.get("is_reserved", False)))
                 for s in e.get("seats", [])]
        evt = Event(event_id=e["event_id"], name=e["name"], date=e["date"], location=e["location"], seats=seats)
        manager.events[evt.event_id] = evt

    # load customers
    for c in data.get("customers", []):
        cust = Customer(customer_id=c["customer_id"], name=c["name"], email=c["email"])
        manager.customers[cust.customer_id] = cust

    # load tickets
    for t in data.get("tickets", []):
        ticket = Ticket(ticket_id=t["ticket_id"],
                        event_id=t["event_id"],
                        seat_id=t["seat_id"],
                        customer_id=t["customer_id"],
                        price=float(t.get("price", 0.0)),
                        created_at=t.get("created_at", ""),
                        status=t.get("status", "booked"))
        manager.tickets[ticket.ticket_id] = ticket
        # mark reserved seats for booked tickets
        if ticket.status == "booked":
            ev = manager.events.get(ticket.event_id)
            if ev:
                try:
                    s = ev.find_seat(ticket.seat_id)
                    s.is_reserved = True
                except Exception:
                    pass

# -------------------------
# XML
# -------------------------
def save_to_xml(manager: BookingManager, filename: str = "data.xml"):
    root = ET.Element("BookingSystem")

    events_el = ET.SubElement(root, "Events")
    for e in manager.events.values():
        e_el = ET.SubElement(events_el, "Event", id=e.event_id)
        ET.SubElement(e_el, "Name").text = e.name
        ET.SubElement(e_el, "Date").text = e.date
        ET.SubElement(e_el, "Location").text = e.location
        seats_el = ET.SubElement(e_el, "Seats")
        for s in e.seats:
            s_el = ET.SubElement(seats_el, "Seat", id=s.seat_id)
            ET.SubElement(s_el, "Row").text = s.row
            ET.SubElement(s_el, "Number").text = str(s.number)
            ET.SubElement(s_el, "Price").text = str(s.price)
            ET.SubElement(s_el, "IsReserved").text = "True" if s.is_reserved else "False"

    customers_el = ET.SubElement(root, "Customers")
    for c in manager.customers.values():
        c_el = ET.SubElement(customers_el, "Customer", id=c.customer_id)
        ET.SubElement(c_el, "Name").text = c.name
        ET.SubElement(c_el, "Email").text = c.email

    tickets_el = ET.SubElement(root, "Tickets")
    for t in manager.tickets.values():
        t_el = ET.SubElement(tickets_el, "Ticket", id=t.ticket_id)
        ET.SubElement(t_el, "EventID").text = t.event_id
        ET.SubElement(t_el, "SeatID").text = t.seat_id
        ET.SubElement(t_el, "CustomerID").text = t.customer_id
        ET.SubElement(t_el, "Price").text = str(t.price)
        ET.SubElement(t_el, "CreatedAt").text = t.created_at
        ET.SubElement(t_el, "Status").text = t.status

    tree = ET.ElementTree(root)
    tree.write(filename, encoding="utf-8", xml_declaration=True)

def load_from_xml(manager: BookingManager, filename: str = "data.xml"):
    try:
        tree = ET.parse(filename)
        root = tree.getroot()
    except FileNotFoundError:
        raise FileNotFoundError(f"XML file '{filename}' not found.")
    except Exception as e:
        raise RuntimeError(f"Error reading XML: {e}")

    # clear
    manager.events.clear()
    manager.customers.clear()
    manager.tickets.clear()

    # events
    events_parent = root.find("Events")
    if events_parent is not None:
        for e_elem in events_parent.findall("Event"):
            ev_id = e_elem.attrib.get("id", "")
            name = e_elem.findtext("Name") or ""
            date = e_elem.findtext("Date") or ""
            location = e_elem.findtext("Location") or ""
            seats = []
            seats_parent = e_elem.find("Seats")
            if seats_parent is not None:
                for s_elem in seats_parent.findall("Seat"):
                    sid = s_elem.attrib.get("id", "")
                    row = s_elem.findtext("Row") or ""
                    number = int(s_elem.findtext("Number") or 0)
                    price = float(s_elem.findtext("Price") or 0.0)
                    is_reserved = (s_elem.findtext("IsReserved") == "True")
                    seats.append(Seat(seat_id=sid, row=row, number=number, price=price, is_reserved=is_reserved))
            evt = Event(event_id=ev_id, name=name, date=date, location=location, seats=seats)
            manager.events[evt.event_id] = evt

    # customers
    cust_parent = root.find("Customers")
    if cust_parent is not None:
        for c_elem in cust_parent.findall("Customer"):
            cid = c_elem.attrib.get("id", "")
            name = c_elem.findtext("Name") or ""
            email = c_elem.findtext("Email") or ""
            manager.customers[cid] = Customer(customer_id=cid, name=name, email=email)

    # tickets
    tickets_parent = root.find("Tickets")
    if tickets_parent is not None:
        for t_elem in tickets_parent.findall("Ticket"):
            tid = t_elem.attrib.get("id", "")
            event_id = t_elem.findtext("EventID") or ""
            seat_id = t_elem.findtext("SeatID") or ""
            customer_id = t_elem.findtext("CustomerID") or ""
            price = float(t_elem.findtext("Price") or 0.0)
            created_at = t_elem.findtext("CreatedAt") or ""
            status = t_elem.findtext("Status") or "booked"
            manager.tickets[tid] = Ticket(ticket_id=tid, event_id=event_id, seat_id=seat_id,
                                          customer_id=customer_id, price=price, created_at=created_at, status=status)
            if status == "booked":
                ev = manager.events.get(event_id)
                if ev:
                    try:
                        s = ev.find_seat(seat_id)
                        s.is_reserved = True
                    except Exception:
                        pass
