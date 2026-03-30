"""Base server class with connection infrastructure and login."""

from __future__ import annotations

import binascii
import hashlib
import http.client as http
import json
import logging
import shutil
from base64 import b64encode
from typing import Any, Dict, Optional
from urllib.parse import urlencode, urlparse

logger = logging.getLogger('urbackup-server-python-api-wrapper')


class _UrbackupServerBase:
    """Low-level connection, session management, and login logic."""

    def __init__(
        self,
        server_url: str,
        server_username: str,
        server_password: str,
    ) -> None:
        self._server_url = server_url
        self._server_username = server_username
        self._server_password = server_password

    # If you have basic authentication via .htpasswd
    server_basic_username: str = ''
    server_basic_password: str = ''

    _session: str = ""
    _logged_in: bool = False
    _lastlogid: int = 0

    # -------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------

    def _get_response(
        self,
        action: str,
        params: Dict[str, Any],
        method: str = "POST",
    ) -> http.HTTPResponse:

        headers: Dict[str, str] = {
            'Accept': 'application/json',
            'Content-Type': 'application/json; charset=UTF-8',
        }

        if self.server_basic_username:
            cred = b64encode(
                (self.server_basic_username + ":" + self.server_basic_password).encode()
            ).decode("ascii")
            headers['Authorization'] = 'Basic %s' % cred

        curr_server_url = self._server_url + "?" + urlencode({"a": action})

        if len(self._session) > 0:
            params["ses"] = self._session

        if method == "GET":
            curr_server_url += "&" + urlencode(params)

        target = urlparse(curr_server_url)

        body = urlencode(params) if method == "POST" else ""

        http_timeout = 10 * 60

        hostname = target.hostname
        if hostname is None:
            raise Exception("No hostname in URL: " + curr_server_url)

        if target.scheme == 'http':
            h = http.HTTPConnection(hostname, target.port, timeout=http_timeout)
        elif target.scheme == 'https':
            h = http.HTTPSConnection(hostname, target.port, timeout=http_timeout)
        else:
            logger.error('Unknown scheme: ' + target.scheme)
            raise Exception("Unknown scheme: " + target.scheme)

        h.request(
            method,
            target.path + "?" + target.query,
            body,
            headers,
        )

        return h.getresponse()

    def _get_json(
        self,
        action: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        if params is None:
            params = {}

        tries = 50

        response = None
        while tries > 0:
            response = self._get_response(action, params)

            if response.status == 200:
                break

            tries -= 1
            if tries == 0:
                return None
            else:
                logger.error("API call failed. Retrying...")

        if response is None:
            return None

        data = response.read()

        response.close()

        return json.loads(data.decode("utf-8", "ignore"))

    def _download_file(
        self,
        action: str,
        outputfn: str,
        params: Dict[str, Any],
    ) -> bool:

        response = self._get_response(action, params, "GET")

        if response.status != 200:
            return False

        with open(outputfn, 'wb') as outputf:
            shutil.copyfileobj(response, outputf)

        return True

    def _md5(self, s: str) -> str:
        return hashlib.md5(s.encode()).hexdigest()

    # -------------------------------------------------------------------
    # Login / session
    # -------------------------------------------------------------------

    def login(self) -> bool:

        if not self._logged_in:

            logger.debug("Trying anonymous login...")

            login = self._get_json("login", {})

            if not login or 'success' not in login or not login['success']:

                logger.debug("Logging in...")

                salt = self._get_json("salt", {"username": self._server_username})

                if not salt or 'ses' not in salt:
                    logger.warning('Username does not exist')
                    return False

                self._session = salt["ses"]

                if 'salt' in salt:
                    password_md5_bin = hashlib.md5(
                        (salt["salt"] + self._server_password).encode()
                    ).digest()
                    password_md5 = binascii.hexlify(password_md5_bin).decode()

                    if "pbkdf2_rounds" in salt:
                        pbkdf2_rounds = int(salt["pbkdf2_rounds"])
                        if pbkdf2_rounds > 0:
                            password_md5 = binascii.hexlify(
                                hashlib.pbkdf2_hmac(
                                    'sha256',
                                    password_md5_bin,
                                    salt["salt"].encode(),
                                    pbkdf2_rounds,
                                )
                            ).decode()

                    password_md5 = self._md5(salt["rnd"] + password_md5)

                    login = self._get_json("login", {
                        "username": self._server_username,
                        "password": password_md5,
                    })

                    if not login or 'success' not in login or not login['success']:
                        logger.warning('Error during login. Password wrong?')
                        return False

                    else:
                        self._logged_in = True
                        return True
                else:
                    return False
            else:
                self._logged_in = True
                self._session = login["session"]
                return True
        else:

            return True
