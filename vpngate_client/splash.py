# -*- coding: utf8 -*-
from tkinter import Tk, PhotoImage, Canvas, NW


class ShowSplash:
    def start(self):
        self.running = True

        # タイトルバー非表示で画面生成
        self.splash = Tk()
        self.splash.overrideredirect(1)

        # モニターの縦横幅取得
        sw = self.splash.winfo_screenwidth()
        sh = self.splash.winfo_screenheight()

        # 画像ロード
        photo = PhotoImage(file="resources/splash.png")

        # 画像の縦横幅取得
        pw = photo.width()
        ph = photo.height()

        # 描画
        canvas = Canvas(width=pw, height=ph)
        canvas.place(x=0, y=0)
        canvas.create_image(0, 0, image=photo, anchor=NW)
        canvas.create_text(pw / 2, ph - 24, text="Loading...", font=("", 24))

        # モニターの中央に画面を表示
        self.splash.geometry(
            str(pw)
            + "x"
            + str(ph)
            + "+"
            + str((sw - pw) // 2)
            + "+"
            + str((sh - ph) // 2)
        )

        self.splash.after(1000, self._check_to_quit)
        self.splash.mainloop()

        # need to delete variables that reference tkinter objects in the thread
        del self.splash

    def _check_to_quit(self):
        if self.running:
            self.splash.after(100, self._check_to_quit)
        else:
            self.splash.destroy()

    def quit(self):
        self.running = False
