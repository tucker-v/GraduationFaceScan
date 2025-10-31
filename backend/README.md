## How to run the backend

go to backend directory

```console
cd backend
```

install required dependencies

```console
pip install -r requirements.txt
```

create .env file in backend directory

```console 
DB_NAME=graduation_facial_recognition
DB_USER=YOUR_USERNAME
DB_PASSWORD=YOUR_PASSWORD
DB_HOST=localhost
DB_PORT=5432
```

start the server

```console
uvicorn app.main:app --reload
```

or

```console
python main.py
```

test server running

```console
curl 127.0.0.1:8000/
```
test database connection
```console
curl 127.0.0.1:8000/students/
```

