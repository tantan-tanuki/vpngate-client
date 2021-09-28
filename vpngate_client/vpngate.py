# -*- coding: utf8 -*-
from urllib import request
from io import StringIO
import base64
import csv
import re
import socket
from concurrent.futures import ThreadPoolExecutor
import sys
from constants import *


# VPNGateからサーバ一覧を取得
def getServerList() -> list:
    req = request.Request("http://www.vpngate.net/api/iphone/")

    with request.urlopen(req) as res:
        # BODYをCSVとして読み込み
        with StringIO() as f:
            f.write(res.read().decode())
            f.seek(0)
            csv_reader = csv.DictReader(f, CSV_HEADER)

            # ヘッダ行の読み飛ばし
            next(csv_reader)
            next(csv_reader)

            # サーバリストの生成
            tpe = ThreadPoolExecutor(max_workers=20)
            rows = []
            for row in csv_reader:
                if (row[HOST_NAME] != "*") & (len(row) == 15):
                    # 接続確認に時間がかかるのでスレッドプールにて実行
                    tpe.submit(checkConfig, rows, row)
            tpe.shutdown()

            # 生成したサーバリストを返す
            return rows


def checkConfig(rows, row):
    try:
        # 接続先情報取得
        config = base64.b64decode(row[OPENVPN_CONFIG_DATA]).decode()
        ip, port = re.findall("remote (.*) (.*)\r", config)[1]
        proto = re.findall("proto (.*)\r", config)[1]

        # ネットワーク接続確認(UDPって確認できるんかな。。。)
        if "tcp" == str(proto):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(3)
            s.connect((ip, int(port)))
            s.close()

        # ソケットがOPEN出来たのでリストに追加
        row[OPENVPN_CONFIG_DATA] = config
        row[PROTOCOL] = proto
        rows.append(row)

    except Exception as e:
        print(str(ip) + ":" + str(port) + ":" + str(e), file=sys.stderr)
