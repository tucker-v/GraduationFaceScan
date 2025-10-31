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
#### Open "http://127.0.0.1:8000/" to view API

### test server running

```console
curl 127.0.0.1:8000/
```

### test database connection
```console
curl 127.0.0.1:8000/students/
```

### Open "web/admin.html" in browser
http://127.0.0.1:5500/web/admin.html 
- (Might not work, I'm using live server VSCode extension)

### *Use pgAdmin 4 to view database and double check everything*
## How to shutdown everything

### CTRL + C in your terminal to shutdown API server

### To delete DB (After Stopping API Server)
```console
python shutDown.py
```

