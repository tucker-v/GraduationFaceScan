## How to setup everything


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
python setup.py
```

### test server running

```console
curl 127.0.0.1:8000/
```

### test database connection
```console
curl 127.0.0.1:8000/students/
```

### Open "web/admin.html" in browser

## How to shutdown everything
### CTRL + C in your terminal to shutdown API server
### To delete DB (After Stopping API Server)
```console
python shutDown.py
```

