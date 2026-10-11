Cinema Seat Reservation API

A beginner backend project built with Python, FastAPI and SQLite. It lets a cinema record its customers and reserve seats for them.

Purpose

This project is a backend API for managing cinema customers and their seat reservations. It was built to practice the basics of backend development:

creating Python classes (Pydantic models) to validate request and response data
writing SQL queries against a SQLite database
creating REST API endpoints in FastAPI
linking two tables together with a foreign key
Scope

Included features

Create, view, list, update and delete customers
Reserve a seat for an existing customer
Prevent the same seat from being reserved twice (returns "Seat already reserved")
Check that a customer exists before a reservation is made
Validate input: names and seat numbers cannot be empty, ages cannot be negative
Show each customer's reservation (reservation ID and seat number) in the customer list
Delete a customer's reservations automatically when the customer is deleted
Try every endpoint in the browser at /docs

Not included

Movies, showtimes or multiple screens (a seat is just a label such as "A1")
Listing or cancelling a single reservation
Payments, login or user accounts
Run it on Windows

From the project folder (the one that contains main.py), create and activate a virtual environment, then install the dependencies:

powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload

Then open http://127.0.0.1:8000/docs in your browser. The API docs page lets you try every endpoint without writing a separate client.

To stop the server, click the terminal and press Ctrl + C.

If you change a table definition in app/database.py, delete cinema.db and start the app again so the tables are rebuilt.

Project structure
main.py creates the FastAPI app and defines the routes.
app/database.py opens SQLite connections and creates the tables.
app/models.py defines the Pydantic data classes and the SQL helper methods.
cinema.db is the SQLite database file, created the first time the app runs.
Database tables
Table	Columns
customers	id, name, age
reservations	reservation_id, seat_number (unique), customer_id (links to customers.id)
Endpoint documentation
Endpoint	Parameters	Purpose
GET /	None	Displays a welcome message
GET /customers	None	Lists all customers, with their reservation ID and seat number if they have one
GET /customers/{customer_id}	customer_id: int	Displays one customer's information based on id. Returns 404 if not found
POST /customer	customer: CustomerInput (name: str, age: int)	Creates a customer in the database with an id, name and age
PUT /customer/{customer_id}	customer_id: int, customer: CustomerInput	Updates a customer's name and age. Returns 404 if not found
DELETE /customer/{customer_id}	customer_id: int	Deletes a customer and all of their reservations. Returns 404 if not found
POST /reservation	payload: ReservationInput (seat_number: str, customer_id: int)	Reserves a seat for an existing customer. Returns 404 if the customer does not exist, or 409 if the seat is already taken
Example requests

Create a customer (POST /customer):

json
{ "name": "Ana", "age": 20 }

Reserve a seat for that customer (POST /reservation):

json
{ "seat_number": "A1", "customer_id": 1 }

Reserving "A1" a second time returns:

json
{ "detail": "Seat already reserved" }
