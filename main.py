"""Create the FastAPI app and connect its route modules."""

import sqlite3

from fastapi import FastAPI, HTTPException

from app.database import database_connection, initialize_database
from app.models import Customer, CustomerInput, ReservationInput

app = FastAPI(title="Cinema Seat Reservation API", version="1.0.0")


@app.get("/")
def home():
    return {"message": "Welcome! Visit /docs to try the API."}


@app.get("/customers")
def get_customers():
    result = Customer.list_customers(database_connection=database_connection)
    return {"customers": result}


@app.get("/customers/{customer_id}")
def get_customer(customer_id: int):
    result = Customer.get_customer(
        customer_id=customer_id, database_connection=database_connection
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"customer": result}


@app.post("/customer")
def create_customer(customer: CustomerInput):
    result = Customer.create_customer(
        customer_input=customer, database_connection=database_connection
    )
    return {"customer": result}


@app.put("/customer/{customer_id}")
def edit_customer(customer_id: int, customer: CustomerInput):
    result = Customer.update_customer(
        customer_id=customer_id,
        customer_input=customer,
        database_connection=database_connection,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"customer": result}


@app.delete("/customer/{customer_id}")
def delete_customer(customer_id: int):
    deleted = Customer.delete_customer(
        customer_id=customer_id, database_connection=database_connection
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Customer not found")
    return {"message": "Customer deleted successfully"}


@app.post("/reservation")
def create_reservation(payload: ReservationInput):
    customer = Customer.get_customer(
        customer_id=payload.customer_id, database_connection=database_connection
    )
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    try:
        result = ReservationInput.create_reservation(
            reservation_input=payload, database_connection=database_connection
        )
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Seat already reserved")

    return {"reservation": result}


initialize_database()
