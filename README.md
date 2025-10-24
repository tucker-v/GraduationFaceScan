# GraduationFaceScan
Allows faculty and staff to check in students for graduation via a face scan using a database.


## How to View
You can view your PostgreSQL database in several ways depending on your preference — graphical interface, command line, or Python.
Below are step-by-step methods that work perfectly with your project setup.


### Option 1: Using pgAdmin 4 (Graphical Interface — Recommended)
pgAdmin is the easiest way to visualize your database, tables, and data.

#### Steps:
- Open pgAdmin 4

    - It should be installed with PostgreSQL automatically.

    - You can search for “pgAdmin 4” in your Start Menu.

- Connect to Your PostgreSQL Server

- On the left panel, expand "Servers."

- Click the one labeled PostgreSQL 15 (or 16).

- Enter your PostgreSQL password (same one used in your db_config.json).

- Find Your Database

- Expand Databases.

- Look for graduation_facial_recognition (the one created by your script).

- View Tables

- Expand:

- Databases → graduation_facial_recognition → Schemas → public → Tables
- You’ll see all six tables:

    - STUDENT

    - STAFF

    - CEREMONY

    - FACE_IMAGE

    - MANAGES

    - QUEUED

- View Data

- Right-click on a table (e.g., STUDENT).

- Choose View/Edit Data → All Rows.

- This opens a spreadsheet-like view of your data.

- View Table Structure

- Right-click on a table → Properties → Columns tab

- You’ll see all column names, data types, and keys.

- Take Screenshots

### For Assignment
- For your assignment, capture:

- The full database connected in pgAdmin.

- Tables with data shown.

- Table structure showing primary and foreign keys.


### Option 2: Using Command Line (psql)
This is great for quick access or debugging.

#### Steps:
- Open Command Prompt (Windows) or Terminal (Mac/Linux).

- Log in to PostgreSQL:

    - bash
    - psql -U postgres
    - (Replace postgres with your username.)

- Connect to Your Database:

    - sql
    - \c graduation_facial_recognition
- List Tables:

    - sql
    - \dt
- View Data in a Table:

    - sql
    - SELECT * FROM student;
    - SELECT * FROM queued;
- View Table Schema:

    - sql
    - \d student
- Quit PostgreSQL:

    - sql
    - \q