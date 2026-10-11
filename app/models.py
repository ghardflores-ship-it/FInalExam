"""Data models used to validate API input and output."""

from pydantic import BaseModel, Field


class CustomerInput(BaseModel):
    """Fields a customer can send when creating or updating a record."""

    name: str = Field(min_length=1)
    age: int = Field(ge=0)

    @staticmethod
    def list_customers(database_connection):
        with database_connection() as connection:
            rows = connection.execute(
                """SELECT
                    c.id,
                    c.name,
                    c.age,
                    r.reservation_id,
                    r.seat_number
                FROM customers c
                LEFT JOIN reservations r ON c.id = r.customer_id
                ORDER BY c.id"""
            ).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def create_customer(customer_input, database_connection):
        with database_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO customers (name, age) VALUES (?, ?)",
                (customer_input.name, customer_input.age),
            )
            row = connection.execute(
                "SELECT id, name, age FROM customers WHERE id = ?",
                (cursor.lastrowid,),
            ).fetchone()
        return dict(row)

    @staticmethod
    def get_customer(customer_id, database_connection):
        with database_connection() as connection:
            row = connection.execute(
                "SELECT id, name, age FROM customers WHERE id = ?", (customer_id,)
            ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def update_customer(customer_id, customer_input, database_connection):
        with database_connection() as connection:
            connection.execute(
                "UPDATE customers SET name = ?, age = ? WHERE id = ?",
                (customer_input.name, customer_input.age, customer_id),
            )
            row = connection.execute(
                "SELECT id, name, age FROM customers WHERE id = ?", (customer_id,)
            ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def delete_customer(customer_id, database_connection):
        with database_connection() as connection:
            # Remove their reservations first, otherwise the foreign key blocks the delete
            connection.execute(
                "DELETE FROM reservations WHERE customer_id = ?", (customer_id,)
            )
            connection.execute("DELETE FROM customers WHERE id = ?", (customer_id,))


class Customer(CustomerInput):
    """A customer record returned by the API."""

    id: int


class ReservationInput(BaseModel):
    """Fields required to create a seat reservation."""

    seat_number: str = Field(min_length=1)
    customer_id: int = Field(ge=1)

    @staticmethod
    def create_reservation(reservation_input, database_connection):
        with database_connection() as connection:
            cursor = connection.execute(
                "INSERT INTO reservations (seat_number, customer_id) VALUES (?, ?)",
                (reservation_input.seat_number, reservation_input.customer_id),
            )
            row = connection.execute(
                """SELECT reservation_id, seat_number, customer_id
                FROM reservations WHERE reservation_id = ?""",
                (cursor.lastrowid,),
            ).fetchone()
        return dict(row)


class Reservation(ReservationInput):
    """A reservation record returned by the API."""

    reservation_id: int