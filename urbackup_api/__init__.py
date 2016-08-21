import http.client as http
import json
from urllib.parse import urlparse
from urllib.parse import urlencode
from base64 import b64encode
import hashlib
import socket
import shutil
import os
import binascii

class urbackup_server:
    
    def __init__(self, server_url, server_username, server_password):
        self._server_url=server_url
        self._server_username=server_username
        self._server_password=server_password
    

    #If you have basic authentication via .htpasswd
    server_basic_username = ''
    server_basic_password = ''
    
    
    _session=""
    
    _logged_in = False
    
    def _get_response(self, action, params, method="POST"):
                
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=UTF-8'
        }
        
        if('server_basic_username' in globals() and len(self.server_basic_username)>0):
            userAndPass = b64encode(str.encode(self.server_basic_username+":"+self.server_basic_password)).decode("ascii")
            headers['Authorization'] = 'Basic %s' %  userAndPass
        
        curr_server_url=self._server_url+"?"+urlencode({"a": action});
        
        if(len(self._session)>0):
            params["ses"]=self._session
            
        if method==None:
            method = 'POST'
        
        if method=="GET":
            curr_server_url+="&"+urlencode(params);
        
        target = urlparse(curr_server_url)
            
        if method=='POST':
            body = urlencode(params)
        else:
            body = ''
        
        http_timeout = 10*60;
        
        if(target.scheme=='http'):
            h = http.HTTPConnection(target.hostname, target.port, timeout=http_timeout)
        elif(target.scheme=='https'):
            h = http.HTTPSConnection(target.hostname, target.port, timeout=http_timeout)
        else:
            print('Unkown scheme: '+target.scheme)
            raise Exception("Unkown scheme: "+target.scheme)
        
        h.request(
                method,
                target.path+"?"+target.query,
                body,
                headers)
        
        return h.getresponse();
    
    def _get_json(self, action, params = {}):     
        tries = 50
        
        while tries>0:
            response = self._get_response(action, params)
        
            if(response.status == 200):
                break
            
            tries=tries-1
            if(tries==0):
                return None
            else:
                print("API call failed. Retrying...")
        
        data = response.readall();
        
        response.close()
            
        return json.loads(data.decode("utf-8"))
    
    def _download_file(self, action, outputfn, params):
        
        response = self.get_response(action, params, "GET");
        
        if(response.status!=200):
            return False
        
        with open(outputfn, 'wb') as outputf:
            shutil.copyfileobj(response, outputf)
            
        
        return True        
    
    def _md5(self, s):
        return hashlib.md5(s.encode()).hexdigest()
    
    def login(self):
        
        if( not self._logged_in):
            
            print("Trying anonymous login...")
            
            login = self._get_json("login", {});
            
            if(not login or 'success' not in login or not login['success']):
                            
                print("Logging in...")
            
                salt = self._get_json("salt", {"username": self._server_username})
                
                if( not salt or not ('ses' in salt) ):
                    print('Username does not exist')
                    return False
                    
                self._session = salt["ses"];
                    
                if( 'salt' in salt ):
                    password_md5_bin = hashlib.md5((salt["salt"]+self._server_password).encode()).digest()
                    password_md5 = binascii.hexlify(password_md5_bin).decode()
                    
                    if "pbkdf2_rounds" in salt:
                        pbkdf2_rounds = int(salt["pbkdf2_rounds"])
                        if pbkdf2_rounds>0:
                            password_md5 = binascii.hexlify(hashlib.pbkdf2_hmac('sha256', password_md5_bin, 
                                                               salt["salt"].encode(), pbkdf2_rounds)).decode()
                    
                    password_md5 = self._md5(salt["rnd"]+password_md5)
                    
                    login = self._get_json("login", { "username": self._server_username,
                                                "password": password_md5 })
                    
                    if(not login or 'success' not in login or not login['success']):
                        print('Error during login. Password wrong?')
                        return False
                    
                    else:
                        self._logged_in=True
                        return True
                else:
                    return False
            else:
                self._logged_in=True
                self._session = login["session"];
                return True                
        else:
            
            return True
        
    
    def get_client_status(self, clientname):
        
        if not self.login():
            return None
        
        status = self._get_json("status")
        
        if not status:
            return None
        
        if not "status" in status:
            return None
        
        for client in status["status"]:
                
            if (client["name"] == clientname):
                
                return client;
            
        print("Could not find client status. No permission?")
        return None
    
    def download_installer(self, installer_fn, new_clientname):
        
        if not self.login():
            return False
        
        new_client = self._get_json("add_client", { "clientname": new_clientname})
        
        if "already_exists" in new_client:
            
            status = self.get_client_status(new_clientname)
            
            if status == None:
                return False
            
            return self._download_file("download_client", installer_fn,
                                 {"clientid": status["id"] })
        
        
        if not "new_authkey" in new_client:     
            return False
        
        return self._download_file("download_client", installer_fn,
                             {"clientid": new_client["new_clientid"],
                              "authkey": new_client["new_authkey"]
                              })
                
    def add_client(self, clientname):
        
        if not self.login():
            return None
                
        ret = self._get_json("add_client", { "clientname": clientname})
        if ret==None or "already_exists" in ret:
            return None
        
        return ret
    
    def get_global_settings(self):
        if not self.login():
            return None
        
        settings = self._get_json("settings", {"sa": "general"} )
        
        if not settings or not "settings" in settings:
            return None
        
        return settings["settings"]
    
    def set_global_setting(self, key, new_value):
        if not self.login():
            return False
        
        settings = self._get_json("settings", {"sa": "general"} )
        
        if not settings or not "settings" in settings:
            return False
        
        settings["settings"][key] = new_value
        settings["settings"]["sa"] = "general_save"
        
        ret = self._get_json("settings", settings["settings"])
        
        return ret!=None and "saved_ok" in ret
    
    def get_client_settings(self, clientname):
        
        if not self.login():
            return None
        
        client = self.get_client_status(clientname)
        
        if client == None:
            return None
        
        clientid = client["id"];
        
        settings = self._get_json("settings", {"sa": "clientsettings",
                                    "t_clientid": clientid})
        
        if not settings or not "settings" in settings:
            return None
            
        return settings["settings"]
    
    def change_client_setting(self, clientname, key, new_value):
        if not self.login():
            return False
        
        client = self.get_client_status(clientname)
        
        if client == None:
            return False
        
        clientid = client["id"];
        
        settings = self._get_json("settings", {"sa": "clientsettings",
                                    "t_clientid": clientid})
        
        if not settings or not "settings" in settings:
            return False
        
        settings["settings"][key] = new_value
        settings["settings"]["overwrite"] = "true"
        settings["settings"]["sa"] = "clientsettings_save"
        settings["settings"]["t_clientid"] = clientid
        
        ret = self._get_json("settings", settings["settings"])
        
        return ret!=None and "saved_ok" in ret
        
    def get_client_authkey(self, clientname):
        
        if not self.login():
            return None
        
        settings = self.get_client_settings(clientname)
        
        if settings:
            return settings["internet_authkey"]
        
        return None
    
    def get_server_identity(self):
        
        if not self.login():
            return None
    
        status = self._get_json("status")
        
        if not status:
            return None
        
        if not "server_identity" in status:
            return None
        
        return status["server_identity"]
    
    def get_status(self):
        if not self.login():
            return None
        
        status = self._get_json("status")
        
        if not status:
            return None
        
        if not "status" in status:
            return None
        
        return status["status"]
    
    def get_extra_clients(self):
        if not self.login():
            return None
        
        status = self._get_json("status")
        
        if not status:
            return None
        
        if not "extra_clients" in status:
            return None
        
        return status["extra_clients"]
    
    def _start_backup(self, clientname, backup_type):
        
        client_info = self.get_client_status(clientname)
        
        if not client_info:
            return False
        
        ret = self._get_json("start_backup", {"start_client": client_info["id"], 
                                         "start_type": backup_type } );
                                        
        if ( ret==None 
            or "result" not in ret
            or len(ret["result"])!=1
            or "start_ok" not in ret["result"][0]
            or not ret["result"][0]["start_ok"] ):
            return False
        
        return True
    
    def start_incr_file_backup(self, clientname):
        return self._start_backup(clientname, 'incr_file');
    
    def start_full_file_backup(self, clientname):
        return self._start_backup(clientname, 'full_file');
    
    def start_incr_image_backup(self, clientname):
        return self._start_backup(clientname, 'incr_image');
    
    def start_full_image_backup(self, clientname):
        return self._start_backup(clientname, 'full_image');
    
    def add_extra_client(self, addr):
        if not self.login():
            return None
        
        ret = self._get_json("status", {"hostname": addr } );
                                        
        if not ret:
            return False
        
        return True
    
    def remove_extra_client(self, ecid):
        if not self.login():
            return None
        
        ret = self._get_json("status", {"hostname": ecid,
                                        "remove": "true" } );
                                        
        if not ret:
            return False
        
        return True
        
