## How to setup everything

```console 
Make sure you have C++ Build Tools installed and also have
pgvector installed on your computer.

```


### Create .env file

```console 
DB_NAME=graduation_facial_recognition
DB_USER=YOUR_USERNAME
DB_PASSWORD=YOUR_PASSWORD
DB_HOST=localhost
DB_PORT=5432
```

### Create db_config.json file

```console 
{
    "dbname": "graduation_facial_recognition",
    "user": "YOUR_USERNAME",
    "password": "YOUR_PASSWORD",
    "host": "localhost",
    "port": "5432"
}
```

### Run
```console
cd frontend
npm run build
cd ..
python setup.py


P.S admin credentials:
user: admin
pass: ChangeMeNow123!

```
#### Open "http://127.0.0.1:8000/" to view API

### test server running

```console
curl 127.0.0.1:8000/
```
## How to shutdown everything

### CTRL + C in your terminal to shutdown API server

### To delete DB (After Stopping API Server)
```console
python shutDown.py
```

