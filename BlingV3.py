#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Set 4 2023.

@author: MatheusBruno
"""
from dotenv import dotenv_values

import datetime
import requests
import base64
import os


class BlingV3():
    """Facilitate and obtain the Bling API V3 Access Token."""

    def parmentHeader(self, path: str = None):
        """
        Enter the path of the txt file with the client_id and client_secret.

        Example:
        -------
        client_id:sequence of numbers,
        client_secret:sequence of numbers

        :Usage:
            ::
                Bling().parmentHeader('/home/user/document/credential.txt')
                or
                Bling().parmentHeader() whit .env
        """
        global header

        if path:
            credential = None

            with open(path, 'r') as file:
                credential = file.read()
                file.close()

            listCredential = credential.split(',')

            listCredential[0] = listCredential[0].replace("client_id:", "")
            listCredential[1] = listCredential[1].replace(
                "\nclient_secret:", ""
            )
        else:
            listCredential = [
                dotenv_values()["BLING_CLIENT_ID"],
                dotenv_values()["BLING_CLIENT_SECRET"]
            ]

        credentialbs4 = f"{listCredential[0]}:{listCredential[1]}"
        credentialbs4 = credentialbs4.encode('ascii')
        credentialbs4 = base64.b64encode(credentialbs4)
        credentialbs4 = bytes.decode(credentialbs4)

        header = {
            'Accept': '1.0',
            'Authorization': f'Basic {credentialbs4}'
        }

    def paramentCode(self, code: str):
        """
        Provide url code.

        :Usage:
            ::
                Bling().paramentCode("8337d4fd498508b9225b695f3bdf0ad086fb8bcc")
        """
        global dice
        dice = {
            'grant_type': 'authorization_code',
            'code': code
        }

    def tokenApi(self, save_txt: bool = False):
        """
        Return a list of objects containing the api data in case of right.

        Parameters
        ----------
        save_txt : bool
            Save the credentials to a txt file (True)

        [access_toke, expires_in, token_type, scope, refresh_token]
        in case of any error
        [error]
        ------------------------------------------------------------------
        If successful, a file will be created with the credentials and time.

        :Usage:
            ::

                obj = Bling().tokenApi()
        """
        api = requests.post(
            'https://www.bling.com.br/Api/v3/oauth/token',
            headers=header, json=dice
        )
        situationStatusCode = api.status_code
        print(situationStatusCode)
        api = api.json()

        if situationStatusCode == 400:
            return api
        elif save_txt:
            self._saveTXTCredential(api)

        return self._objCredentials(api)

    def refreshToken(self, refresh_token: str, save_txt: bool = False):
        """
        Return the new access token and update the file with the credentials.

        Parameters
        ----------
        refresh_token : str
            Crendital refresh token
        save_txt : bool
            Save the credentials to a txt file (True) or save to .env (False)

        :Usage:
            ::
                obj = Bling().refreshToken("access_token")
        """
        dice = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        api = requests.post(
            'https://www.bling.com.br/Api/v3/oauth/token',
            headers=header, json=dice
        )
        situationStatusCode = api.status_code
        print(situationStatusCode)
        api = api.json()

        if situationStatusCode == 400:
            return api
        elif save_txt:
            self._saveTXTCredential(api)

        return self._objCredentials(api)

    def _objCredentials(self, api):
        """
        Return credentials obj.

        Parameters
        ----------
        api : TYPE
            DESCRIPTION.

        Returns
        -------
        dict
            DESCRIPTION.

        """
        return {
            'access_token': api['access_token'],
            'expires_in': api['expires_in'],
            'token_type': api['token_type'],
            'scope': api['scope'],
            'refresh_token': api['refresh_token']
        }

    def _saveTXTCredential(self, api):
        """
        Save the credentials to a txt file in the "credential" directory.

        Parameters
        ----------
        api : TYPE
            DESCRIPTION.

        Returns
        -------
        dict
            DESCRIPTION.

        """
        path = os.getcwd()
        dateNow = datetime.date.today()
        apiHoursNow = ((int(api['expires_in'])/60)/60)
        systemHoursNow = datetime.datetime.now()
        hoursExpiration = (
            int(systemHoursNow.strftime("%H")) + apiHoursNow
        )

        if os.path.isdir(f"{path}/credential"):
            pass
        else:
            os.mkdir(f'{path}/credential')

        with open(f"{path}/credential/dice.txt", 'w') as file:
            file.write(f"""access_token:{api['access_token']},
                           \rexpires_in:{api['expires_in']},
                           \rhoursExpiration:{hoursExpiration},
                           \rdateExpiration:{dateNow},
                           \rrefresh_token:{api['refresh_token']}""")
            file.close()
