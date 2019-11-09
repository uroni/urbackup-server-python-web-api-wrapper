import urbackup_api


server = urbackup_api.urbackup_server("http://127.0.0.1:55414/x", "admin", "foo")

for action in server.get_actions():
    a = action["action"]
    if a ==server.action_full_file or a==server.action_resumed_full_file:
        print("Running full file backup: "+action["name"])
        
        print("Stopping...")
        server.stop_action(action)