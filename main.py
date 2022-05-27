import asyncio
import logging
import os
import sys
from discord import Client, AuthFailure, NotFound, Forbidden, HTTPException

from parse_data import parse_tokens_from_file, parse_http_proxies_from_file

file_log = logging.FileHandler('./log.txt')
console_out = logging.StreamHandler()
logging.basicConfig(format=u'%(filename)s [LINE:%(lineno)d] #%(levelname)-8s [%(asctime)s]  %(message)s', level=logging.WARNING, handlers=(file_log, console_out))


class MyClient(Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.guild_id: int = kwargs.get("guild_id")
        self.channel_id: int = kwargs.get("channel_id")
        self.message_id: int = kwargs.get("message_id")
        self.emoji: str = kwargs.get("emoji")
        self.account_number: int = kwargs.get("account_number")
        self.count_accounts: int = kwargs.get("count_accounts")

    async def on_ready(self):
        logging.warning(f"[{self.account_number}/{self.count_accounts}] Successfully logged as {self.user}")

        try:
            guild_name = await self.fetch_guild(self.guild_id)
        except (Exception,) as e:
            logging.error(f"[{self.account_number}/{self.count_accounts}] [ERROR] Аккаунта {self.user} нету на сервере {self.guild_id}.")
            await self.close()
            return

        logging.warning(f"[{self.account_number}/{self.count_accounts}] Добавляю реакцию аккаунтом {self.user} для сервера {guild_name}...")

        try:
            await self.http.add_reaction(channel_id=self.channel_id, message_id=self.message_id, emoji=self.emoji)
            logging.warning(f"[{self.account_number}/{self.count_accounts}] [SUCCESS] Реакция аккаунтом {self.user} для сервера {self.guild_id} поставлена!")
        except NotFound:
            logging.warning(f"[{self.account_number}/{self.count_accounts}] Неправильный ID сервера/канала/сообщения. Реакция аккаунтом {self.user} для сервера {self.guild_id} не была поставлена.")

        except Forbidden:
            logging.warning(f"[{self.account_number}/{self.count_accounts}] У аккаунта нету прав на это действие. Реакция аккаунтом {self.user} для сервера {self.guild_id} не была поставлена.")

        except HTTPException as e:
            logging.warning(f"[{self.account_number}/{self.count_accounts}] Ошибка >> {e}. Реакция аккаунтом {self.user} для сервера {self.guild_id} не была поставлена.")

        except Exception as e:
            logging.error(f"[{self.account_number}/{self.count_accounts}] Ошибка >> {e}")

        await self.close()


def parse_answer_to_bool(answer: str) -> bool:
    answer = answer.strip().lower()
    if answer == "yes" or answer == "y" or answer == "":
        return True
    else:
        return False


async def start():
    os.system("cls||clear")  # Чистим консоль на Windows и Linux

    print("""░██████╗░██╗██╗░░░██╗███████╗░█████╗░░██╗░░░░░░░██╗░█████╗░██╗░░░██╗
██╔════╝░██║██║░░░██║██╔════╝██╔══██╗░██║░░██╗░░██║██╔══██╗╚██╗░██╔╝
██║░░██╗░██║╚██╗░██╔╝█████╗░░███████║░╚██╗████╗██╔╝███████║░╚████╔╝░
██║░░╚██╗██║░╚████╔╝░██╔══╝░░██╔══██║░░████╔═████║░██╔══██║░░╚██╔╝░░
╚██████╔╝██║░░╚██╔╝░░███████╗██║░░██║░░╚██╔╝░╚██╔╝░██║░░██║░░░██║░░░
░╚═════╝░╚═╝░░░╚═╝░░░╚══════╝╚═╝░░╚═╝░░░╚═╝░░░╚═╝░░╚═╝░░╚═╝░░░╚═╝░░░

created by @crypto_satana | @scissor_eth\n""")

    kwargs_dict = {}

    count_tokens: int = int(input("Введи сколько аккаунтов использовать >> ").strip())
    use_proxy: bool = parse_answer_to_bool(input("Использовать прокси (Y/n)? >> ").strip().lower())
    tokens_list: list[str] = parse_tokens_from_file("tokens.txt")[:count_tokens]  # Парсим токены из файла
    count_accounts = len(tokens_list)

    if use_proxy:
        proxies_list: list[str] = parse_http_proxies_from_file(path="proxies.txt")  # Парсим прокси к аккаунтам из файла
        if len(proxies_list) < count_accounts:
            logging.error("[ERROR] Количество прокси не совпадает с количеством токенов!")
            sys.exit()

    kwargs_dict["guild_id"] = int(input("Введи ID сервера с капчей >> ").strip())
    kwargs_dict["channel_id"] = int(input("Введи ID канала с капчей >> ").strip())  # ID канала на сервере
    kwargs_dict["message_id"]: int = int(input("Введи ID сообщения c капчей >> ").strip())  # ID сообщение на которое нужно ставить реакцию
    kwargs_dict["emoji"] = input("Введи emoji >> ").strip()  # Реакция которую надо поставить. Пример ввода: ✅
    kwargs_dict["count_accounts"] = count_accounts

    for account_number, client_token in enumerate(tokens_list):  # Проходимся по списку токенов. number - индекс в списке, client_token - сам токен
        kwargs_dict["account_number"] = account_number + 1

        if use_proxy:
            proxy_url = proxies_list[account_number]  # Берем прокси соответсвующий дискорд аккаунту
            client = MyClient(token=client_token, proxy_url=proxy_url, **kwargs_dict)  # Запуск клиента с прокси
        else:
            client = MyClient(token=client_token, **kwargs_dict)  # Запуск клиента без прокси

        try:
            await client.login(client_token)  # Пытаемся залогиниться по токену
            await client.connect()  # И приконектиться и запустить on_ready

        except AuthFailure:
            logging.warning(f"[НЕВАЛИДНЫЙ ТОКЕН] [{account_number + 1}/{count_accounts}] Токен {client_token} просрочен или не работает прокси.")


loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
loop.run_until_complete(start())
