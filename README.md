inema Seat Reservation API
This repository is a backend API and database app built in Python with FastAPI and SQLite. It lets a cinema record its customers and reserve seats for them. It shows the basic pattern for:

creating Python classes for request and response data
writing SQL queries against SQLite
creating REST API endpoints in FastAPI
linking two tables together with a foreign key
Purpose
This project is a backend API for managing cinema customers and their seat reservations. It was built to practice the basics of backend development: validating data with Pydantic models, storing it in a SQLite database with SQL queries, and exposing it through REST endpoints in FastAPI.

Scope
Included features

Create, view, list, update and delete customers
Reserve a seat for an existing customer
Prevent the same seat from being reserved twice (returns "Seat already reserved")
Check that a customer exists before a reservation is made
Validate input: names and seat numbers cannot be empty, ages cannot be negative
Show each customer's reservation (reservation ID and seat number) in the customer list
Delete a customer's reservations automatically when the customer is deleted
Not included

Movies, showtimes or multiple screens (a seat is just a label such as "A1")
Listing or cancelling a single reservation
Payments, login or user accounts
Run it on Windows
From this folder, create and activate a virtual environment, then install the dependencies:

py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload
Then open http://127.0.0.1:8000/docs in your browser. The API docs page will let you try the project without writing a separate client.

To stop the server, click the terminal and press Ctrl + C.

Project structure
main.py creates the FastAPI app and defines the routes.
app/database.py opens SQLite connections and creates tables.
app/models.py defines the Pydantic data classes and the SQL helper methods.
cinema.db is the SQLite database file created the first time the app runs.
How to make your own classes
The project uses a simple pattern: a Pydantic model describes the data, and the route functions call helper methods on that model.

Example from app/models.py:

from pydantic import BaseModel, Field


class CustomerInput(BaseModel):
    name: str = Field(min_length=1)
    age: int = Field(ge=0)


class Customer(CustomerInput):
    id: int
To make your own class for a different part of the project, follow the same pattern. For example, a movie:

from pydantic import BaseModel, Field


class MovieInput(BaseModel):
    title: str = Field(min_length=1)
    duration_minutes: int = Field(ge=1)


class Movie(MovieInput):
    id: int
A model class is useful because FastAPI can validate incoming JSON automatically and return the data in a consistent format.

How to make your own SQL queries
The database connection is managed in app/database.py:

@contextmanager
def database_connection() -> Iterator[sqlite3.Connection]:
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
Use it like this when you write your own queries:

with database_connection() as connection:
    rows = connection.execute(
        "SELECT id, title, duration_minutes FROM movies WHERE id = ?",
        (movie_id,),
    ).fetchall()
Important ideas:

CREATE TABLE defines a new table.
INSERT adds rows.
SELECT reads data.
UPDATE changes data.
DELETE removes data.
JOIN combines rows from two tables, such as customers and their reservations.
Use ? placeholders instead of string concatenation to keep SQL safe.
PRAGMA foreign_keys = ON makes SQLite enforce foreign keys. Without it, you could reserve a seat for a customer that does not exist.
The two tables in this project, from app/database.py:

connection.execute(
    """
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL CHECK (age >= 0)
    );
    """
)

connection.execute(
    """
    CREATE TABLE IF NOT EXISTS reservations (
        reservation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        seat_number TEXT NOT NULL UNIQUE,
        customer_id INTEGER,
        CONSTRAINT fk_Customer
        FOREIGN KEY (customer_id)
        REFERENCES customers(id)
    );
    """
)
seat_number is UNIQUE, so the same seat cannot be reserved twice. customer_id is a foreign key that links each reservation to a customer.

If you change a table definition, delete cinema.db and start the app again so the tables are rebuilt.

How to make your own endpoints
FastAPI routes live in main.py. Each function is connected to an HTTP method and path using decorators like @app.get, @app.post, @app.put, and @app.delete.

Example:

@app.get("/customers")
def get_customers():
    result = Customer.list_customers(database_connection=database_connection)
    return {"customers": result}


@app.post("/customer")
def create_customer(customer: CustomerInput):
    result = Customer.create_customer(
        customer_input=customer,
        database_connection=database_connection,
    )
    return {"customer": result}
The route function usually does three things:

accept a request body or URL parameter
call a SQL query through a model helper
return JSON for the client
Routes can also return errors with HTTPException. For example, POST /reservation returns 404 if the customer does not exist and 409 if the seat is already taken.

Reuse this pattern for your own project
A good project workflow is:

Create a new model class in app/models.py.
Add a table in app/database.py with CREATE TABLE IF NOT EXISTS.
Add SQL helper methods to your model class.
Add a route in main.py that calls those helper methods.
Test the endpoint in the Swagger UI at /docs.
For example, to add movies to the cinema, create a Movie class, a movies table, helper methods such as list_movies and create_movie, and routes such as GET /movies and POST /movie. The pattern stays the same even when the data changes.

Current example endpoints
This project already includes these routes:

Endpoint	Parameters	Purpose
GET /	None	Displays a welcome message
GET /customers	None	Lists all customers, with their reservation ID and seat number if they have one
GET /customers/{customer_id}	customer_id: int	Displays one customer's information based on id. Returns 404 if not found
POST /customer	customer: CustomerInput (name: str, age: int)	Creates a customer in the database with an id, name and age
PUT /customer/{customer_id}	customer_id: int, customer: CustomerInput	Updates a customer's name and age. Returns 404 if not found
DELETE /customer/{customer_id}	customer_id: int	Deletes a customer and all of their reservations. Returns 404 if not found
POST /reservation	payload: ReservationInput (seat_number: str, customer_id: int)	Reserves a seat for an existing customer. Returns 404 if the customer does not exist, or 409 if the seat is already taken
Example request bodies:

{ "name": "Ana", "age": 20 }
{ "seat_number": "A1", "customer_id": 1 }
