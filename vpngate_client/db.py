# -*- coding: utf8 -*-
import dataset
from constants import *


class DB:
    def __init__(self) -> None:
        self.db = dataset.connect("sqlite:///serverlist.sqlite")
        # テーブル作成
        table = self.db.create_table(
            "server_list", primary_id=IP, primary_type=self.db.types.text
        )
        table.create_column(HOST_NAME, self.db.types.text, primary_key=True)
        table.create_column(IP, self.db.types.text)
        table.create_column(SCORE, self.db.types.integer)
        table.create_column(PING, self.db.types.integer)
        table.create_column(SPEED, self.db.types.integer)
        table.create_column(COUNTRY_LONG, self.db.types.text)
        table.create_column(COUNTRY_SHORT, self.db.types.text)
        table.create_column(NUM_VPN_SESSIONS, self.db.types.text)
        table.create_column(UPTIME, self.db.types.text)
        table.create_column(TOTAL_USERS, self.db.types.text)
        table.create_column(TOTAL_TRAFFIC, self.db.types.text)
        table.create_column(LOG_TYPE, self.db.types.text)
        table.create_column(OPERATOR, self.db.types.text)
        table.create_column(MESSAGE, self.db.types.text)
        table.create_column(OPENVPN_CONFIG_DATA, self.db.types.text)
        table.create_column(PROTOCOL, self.db.types.text)

        # 初期化
        table.delete()
        self.server_list = table

    def __del__(self):
        self.db.close()

    def save(self, rows):
        self.server_list.insert_many(rows)

    def view(self, speed, ping):
        return self.server_list.find(
            Speed={">=": speed * 1000000},
            Ping={"<=": ping},
            order_by=[PROTOCOL, PING, "-" + SPEED],
        )

    def config(self, hostName, ip):
        row = self.server_list.find_one(IP=ip, HostName=hostName)
        return row[OPENVPN_CONFIG_DATA]

    def distinctCountryShort(self):
        return self.server_list.distinct(COUNTRY_SHORT)
