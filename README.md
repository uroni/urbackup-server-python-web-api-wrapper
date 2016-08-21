# urbackup-server-web-api-wrapper
Python wrapper to access and control an UrBackup server

## Installation

Install with:

	pip3 install urbackup-server-web-api-wrapper

## Usage

Start a full file backup:

```python
import urbackup_api

server = urbackup_api.urbackup_server("http://127.0.0.1:55414/x", "admin", "foo")

server.start_full_file_backup("testclient0")
```

List clients with no file backup in the last three days:

```python
import urbackup_api
server = urbackup_api.urbackup_server("http://127.0.0.1:55414/x", "admin", "foo")
clients = server.get_status()
diff_time = 3*24*60*60 # 3 days
for client in clients:    
    if client["lastbackup"]=="-" or client["lastbackup"] < time.time() - diff_time:
            
        if client["lastbackup"]=="-" or client["lastbackup"]==0:
            lastbackup = "Never"
        else:
            lastbackup = datetime.datetime.fromtimestamp(client["lastbackup"]).strftime("%x %X")
                        
        print("Last file backup at {lastbackup} of client {clientname} is older than three days".format(
              lastbackup=lastbackup, clientname=client["name"] ) )
```

