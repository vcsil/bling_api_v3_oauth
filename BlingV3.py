#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Set 4 2023.

@author: vcsil
"""
from typing import Dict, Optional
from dotenv import get_key, find_dotenv, set_key
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

import requests
import logging
import base64
import pytz
import os

log = logging.getLogger(__name__)


class BlingV3():
    """Facilitate and obtain the Bling API V3 Access Token."""

    def parmentHeader(self, path: str = None, use_txt=False):
        """
        Enter the path of the txt or .env file with the client id and secret.

        The method creates the request header. To do this, it searches the
        directory for the file containing the client's 'secret' and 'id'.
        When use_txt is 'True' it does not search in '.env'.

        Example:
        -------
        client_id:sequence of numbers,
        client_secret:sequence of numbers

        :Usage:
            ::
                BlingV3().parmentHeader(
                    '/home/user/document/credential.txt', True)
                or
                BlingV3().parmentHeader() whit .env
        """
        global header, env_path

        if use_txt:
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
            env_path = find_dotenv()
            listCredential = [
                get_key(dotenv_path=env_path, key_to_get="BLING_CLIENT_ID"),
                get_key(dotenv_path=env_path, key_to_get="BLING_CLIENT_SECRET")
            ]

        credentialbs4 = f"{listCredential[0]}:{listCredential[1]}"
        credentialbs4 = credentialbs4.encode('ascii')
        credentialbs4 = base64.b64encode(credentialbs4)
        credentialbs4 = bytes.decode(credentialbs4)

        header = {
            'Accept': '1.0',
            'Authorization': f'Basic {credentialbs4}'
        }
        return header

    def paramentCode(self,
                     code: str,
                     is_refresh_token: bool = False,
                     ) -> Dict[str, Optional[str]]:
        """
        Provide url code.

        :Usage:
            ::
                Bling().paramentCode("8337d4fd498508b9225b695f3bdf0ad086fb8bcc")
        """
        if is_refresh_token:
            grant_type = 'refresh_token'
            name_code = 'refresh_token'
        else:
            grant_type = 'authorization_code'
            name_code = 'code'

        dice = {
            'grant_type': grant_type,
            name_code: code
        }
        return dice

    def tokenApi(self,
                 authorization_code: str,
                 save_txt: bool = False,
                 save_env: bool = False,
                 is_refresh_token: bool = False,
                 ) -> Dict[str, Optional[str]]:
        """
        Return a list of objects containing the api data in case of right.

        Parameters
        ----------
        authorization_code : str
            Authorization code ou token refresh
        save_txt : bool
            Save the credentials to a txt file (True)
        save_env : bool
            Save credentials in .env (True)

        [access_toke, expires_in, token_type, scope, refresh_token]
        in case of any error
        [error]
        ------------------------------------------------------------------
        If successful, a file will be created with the credentials and time.

        :Usage:
            ::
                obj = Bling().tokenApi()
        """
        header = self.parmentHeader()
        dice = self.paramentCode(authorization_code, is_refresh_token)

        api = requests.post(
            'https://www.bling.com.br/Api/v3/oauth/token',
            headers=header, json=dice
        )
        situationStatusCode = api.status_code
        # print(situationStatusCode)
        api = api.json()

        if situationStatusCode == 400:
            log.info(f"Request failed. code: {situationStatusCode}")
            return api
        if save_txt:
            self._saveTXTCredential(api)
        if save_env:
            self._saveENVCredential(api)

        log.info("Created new credentials")
        return self._objCredentials(api)

    def _objCredentials(
            self,
            api: Dict[str, Optional[str]],
            ) -> Dict[str, Optional[str]]:
        """
        Return credentials obj.

        {access_token, expires_in, token_type, scope, refresh_token}

        Parameters
        ----------
        api : TYPE
            api json.

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

    def _calculateHour(self, expires_in: float) -> datetime:
        """
        Calculate exact time for token end.

        Parameters
        ----------
        expires_in : float
            api['expires_in'].

        Returns
        -------
        hoursExpiration : datetime
            exact time

        """
        fuso_horario_brasil = pytz.timezone("America/Sao_Paulo")

        apiHoursNow = ((int(expires_in)/60)/60)
        systemHoursNow = datetime.now(fuso_horario_brasil)
        hoursExpiration = (
            systemHoursNow + timedelta(hours=apiHoursNow)
        )
        return hoursExpiration

    def _saveTXTCredential(self, api):
        """
        Save the credentials to a txt file in the "credential" directory.

        Parameters
        ----------
        api : TYPE
            api json.
        """
        path = os.getcwd()

        if os.path.isdir(f"{path}/credential"):
            pass
        else:
            os.mkdir(f'{path}/credential')

        hoursExpiration = self._calculateHour(api['expires_in'])

        with open(file=f"{path}/credential/dice.txt", mode="w") as file:
            file.write(f"""OAUTH_ACCESS_TOKEN={api['access_token']}
                           OAUTH_EXPIRES_IN={api['expires_in']}
                           OAUTH_HOURS_EXPIRATION={hoursExpiration}
                           OAUTH_REFRESH_TOKEN={api['refresh_token']}
                           OAUTH_SCOPE= {api['scope']}\n""".replace(
                           '                           ', ''))
        log.info('Finish')

    def _saveENVCredential(self, api):
        """
        Save the credentials to a txt file in the "credential" directory.

        Parameters
        ----------
        api : TYPE
            api json.
        """
        hoursExpiration = self._calculateHour(api['expires_in'])

        set_key(env_path, "OAUTH_ACCESS_TOKEN", f"{api['access_token']}")
        set_key(env_path, "OAUTH_EXPIRES_IN", f"{api['expires_in']}")
        set_key(env_path, "OAUTH_HOURS_EXPIRATION", f"{hoursExpiration}")
        set_key(env_path, "OAUTH_REFRESH_TOKEN", f"{api['refresh_token']}")
        set_key(env_path, "OAUTH_SCOPE", f"{api['scope']}")
        log.info('Finish')


def oauth_blingV3(
    save_txt: bool = False,
    save_env: bool = True,
) -> Dict[str, Optional[str]]:
    """
    Obtain the access token automatically. .env or txt required.

    Automates the connection and authorization of the api like bling and
    returns the access token, uses selenium

    Parameters
    ----------
    save_txt : bool, optional
        True if you want to save the credentials in a txt. Default is False.
    save_env : bool, optional
        True if you want to save the credentials in a .env. Default is True.

    Returns
    -------
    Dict[str, Optional[str]]
        Dict with ['access_token'], ['expires_in'], ['token_type'], ['scope'],
        ['refresh_token']
    """
    env_path = find_dotenv()
    log.info('Selenium init')
    # Caminho para o driver do navegador
    driver_path = 'https://www.bling.com.br/Api/v3/oauth/authorize?'
    response_type = 'response_type=code&'
    client_id = 'client_id='
    client_id += get_key(dotenv_path=env_path, key_to_get="BLING_CLIENT_ID")
    state = '&state=vasco'
    driver_path += response_type + client_id + state

    # Inicializar o navegador
    driver = webdriver.Chrome()
    driver.implicitly_wait(2)
    driver.get(driver_path)

    # Login Bling
    bling_usuario = get_key(dotenv_path=env_path,
                            key_to_get='BLING_USUARIO')
    bling_senha = get_key(dotenv_path=env_path,
                          key_to_get='BLING_SENHA_USUARIO')

    # Navegando
    campo_usuario = driver.find_element(
        By.XPATH,
        "/html/body/div/div/div/form/div[1]/input")
    campo_usuario.send_keys(bling_usuario)

    campo_senha = driver.find_element(
        By.XPATH,
        "/html/body/div/div/div/form/div[2]/input")
    campo_senha.send_keys(bling_senha)

    botao_entrar = driver.find_element(
        By.XPATH,
        "/html/body/div/div/div/form/div[5]/button")
    botao_entrar.click()
    try:
        botao_autorizar = driver.find_element(
            By.XPATH,
            "/html/body/div/div/div/div/div[6]/form/button[2]")
        botao_autorizar.click()
    except NoSuchElementException:
        print("Login ja foi autizado\n")
    finally:
        # O Authorization code é enviado por query string
        link_final = driver.current_url
        driver.quit()

    query_string = link_final.split("?")[1]
    log.info('Selenium Finish')
    query_string = query_string.split("&")
    param_dict = {}
    for param in query_string:
        key, value = param.split("=")
        param_dict[key] = value
    log.info('Send credentials')
    return BlingV3().tokenApi(authorization_code=param_dict['code'],
                              save_txt=save_txt,
                              save_env=save_env,
                              is_refresh_token=False)


def oauth_refresh_blingV3(
        refresh_token: str,
        save_txt: bool = False,
        save_env: bool = True
) -> Dict[str, Optional[str]]:
    """Retorna token de acesso a patir do refresh token."""
    log.info('Init')
    return BlingV3().tokenApi(
        authorization_code=refresh_token,
        save_txt=save_txt,
        save_env=save_env,
        is_refresh_token=True
    )


if __name__ == '__main__':
    try:
        oauth_blingV3()
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        input("Aperte enter.")
