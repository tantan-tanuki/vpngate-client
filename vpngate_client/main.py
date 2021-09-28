# -*- coding: utf8 -*-
import threading
import os
import tkinter as tk
from db import DB
from tkinter import ttk, filedialog, PhotoImage
from splash import ShowSplash
from vpngate import getServerList
from constants import *


class MainClass:
    def __init__(self):
        self.db = DB()
        # VPNサーバ一覧を取得
        self.load_serverlist()

        # メインウィンドウの作成
        self.main_win = tk.Tk()
        self.main_win.title("Server List")
        self.main_win.geometry("640x480")

        # 国旗アイコンを読み込む
        self.nationalFlags = {}
        for cname in self.db.distinctCountryShort():
            self.nationalFlags[cname[COUNTRY_SHORT]] = PhotoImage(
                file="resources/" + cname[COUNTRY_SHORT].lower() + ".png"
            )

        # 検索条件(速度、Ping値)
        self.scale_speed = tk.IntVar()
        self.scale_speed.set(10)
        self.scale_ping = tk.IntVar()
        self.scale_ping.set(5)

        # 検索条件設定表示フレーム
        frame = ttk.Frame(self.main_win)
        frame.pack(fill=tk.BOTH)

        # 検索条件文字列の追加
        self.conditionStr = tk.StringVar()
        self.changeCondition()
        self.condition = tk.Label(frame, textvariable=self.conditionStr)
        self.condition.pack(expand=True, fill=tk.BOTH)

        # Speedスライダー
        self.speedLabel = tk.Label(frame, text="速度")
        self.speedLabel.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        scaleSpeed = tk.Scale(
            frame,
            variable=self.scale_speed,
            command=self.changeCondition,
            orient=tk.HORIZONTAL,  # 配置の向き、水平(HORIZONTAL)、垂直(VERTICAL)
            length=250,  # 全体の長さ
            width=10,  # 全体の太さ
            sliderlength=10,  # スライダー（つまみ）の幅
            from_=0,  # 最小値（開始の値）
            to=100,  # 最大値（終了の値）
            resolution=1,  # 変化の分解能(初期値:1)
        )
        scaleSpeed.pack(fill=tk.X, side=tk.LEFT)

        # Ping値スライダー
        self.pingLabel = tk.Label(frame, text="Ping値")
        self.pingLabel.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
        scalePing = tk.Scale(
            frame,
            variable=self.scale_ping,
            command=self.changeCondition,
            orient=tk.HORIZONTAL,  # 配置の向き、水平(HORIZONTAL)、垂直(VERTICAL)
            length=150,  # 全体の長さ
            width=10,  # 全体の太さ
            sliderlength=10,  # スライダー（つまみ）の幅
            from_=0,  # 最小値（開始の値）
            to=50,  # 最大値（終了の値）
            resolution=1,  # 変化の分解能(初期値:1)
        )
        scalePing.pack(fill=tk.X, side=tk.LEFT)

        # 再検索ボタンの追加
        button = tk.Button(frame, text="条件変更", command=self.updateView)
        button.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # ビューの作成
        self.make_treeview()

        self.main_win.mainloop()

    # 検索条件の変更時に表示を更新する
    def changeCondition(self, event=None):
        self.conditionStr.set(
            "速度" + str(self.scale_speed.get()) + "Mbps以上, "
            "Ping値" + str(self.scale_ping.get()) + "ms以下"
        )

    # 検索条件に基づいてビューを更新
    def updateView(self):
        self.my_tree.delete(*self.my_tree.get_children())
        # ビューにデータをセット
        view_list = self.db.view(self.scale_speed.get(), self.scale_ping.get())
        for i, row in enumerate(view_list):
            self.my_tree.insert(
                parent="",
                index="end",
                iid=i,
                image=self.nationalFlags[row[COUNTRY_SHORT]],
                tags=i % 2,
                values=(
                    row[COUNTRY_SHORT],
                    row[HOST_NAME],
                    row[PROTOCOL],
                    row[IP],
                    int(row[SPEED] / 1000000),
                    row[PING],
                ),
            )

    def load_serverlist(self):
        # スプラッシュ画像表示
        splash = ShowSplash()
        thread = threading.Thread(target=splash.start)
        thread.start()

        try:
            # VPNサーバ一覧をDBへ保存
            self.db.save(getServerList())
        except Exception as e:
            print(e)
        finally:
            # スプラッシュ画像を閉じる
            splash.quit()
            thread.join()

    def make_treeview(self):
        self.my_tree = ttk.Treeview(self.main_win)

        # カラム定義
        self.my_tree["columns"] = (
            "Country",
            "Name",
            "protocol",
            "IP",
            "Speed(Mbps)",
            "Ping",
        )
        # self.my_tree["show"] = "headings"

        # カラム情報生成
        self.my_tree.column("#0", anchor=tk.W, width=25)
        self.my_tree.column("Country", anchor=tk.W, width=25)
        self.my_tree.column("Name", anchor=tk.W, width=75)
        self.my_tree.column("protocol", anchor=tk.W, width=40)
        self.my_tree.column("IP", anchor=tk.W, width=90)
        self.my_tree.column("Speed(Mbps)", anchor=tk.W, width=70)
        self.my_tree.column("Ping", anchor=tk.W, width=25)

        # ヘッダ情報生成
        self.my_tree.heading("#0", text="", anchor=tk.W)
        self.my_tree.heading("Country", text="Country", anchor=tk.W)
        self.my_tree.heading("Name", text="Name", anchor=tk.W)
        self.my_tree.heading("protocol", text="protocol", anchor=tk.W)
        self.my_tree.heading("IP", text="IP", anchor=tk.W)
        self.my_tree.heading("Speed(Mbps)", text="Speed(Mbps)", anchor=tk.W)
        self.my_tree.heading("Ping", text="Ping", anchor=tk.W)

        # 表示設定
        self.my_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # ダブルクリック時のアクション設定
        self.my_tree.bind("<Double-1>", self.OnDoubleClick)

        # ビューにデータをセット
        self.updateView()

        # 見にくいので奇数列の色を変える
        self.my_tree.tag_configure(1, background="#CCFFFF")

    # サーバリストのダブルクリック時に保存ダイアログを開く
    def OnDoubleClick(self, event):
        item = self.my_tree.identify("item", event.x, event.y)
        value = self.my_tree.item(item, "values")
        file_name = filedialog.asksaveasfilename(
            initialfile=value[1] + ".ovpn",
            initialdir=os.path.abspath(os.path.dirname(__file__)),
            filetypes=[("", ".ovpn")],
        )
        if len(file_name) != 0:
            f = open(file_name, "w")
            config_data = str(self.db.config(value[1], value[3]))
            f.write(config_data)


if __name__ == "__main__":
    MainClass()
