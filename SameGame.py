import random
import time

import pyxel


class App:
    SCENE_TITLE_INIT = 100
    SCENE_TITLE_LOOP = 101
    SCENE_TITLE_END = 190

    SCENE_GAME_INIT = 200
    SCENE_GAME_LOOP = 201
    SCENE_GAME_CLICK = 210
    SCENE_GAME_REMOVE = 211
    SCENE_GAME_REMOVE_LOOP = 212
    SCENE_GAME_ALLDOWN_INIT = 220
    SCENE_GAME_ALLDOWN_LOOP = 221
    SCENE_GAME_ALLDOWN_END = 222
    SCENE_GAME_SPWAN = 230
    SCENE_GAME_END = 290

    DRAW_REQUEST_TITLECLEARSCREEN = 100
    DRAW_REQUEST_TITLESTRING = 101
    DRAW_REQUEST_TITLEPUSHSTART = 102
    DRAW_REQUEST_GAMECLEARSCREEN = 200
    DRAW_REQUEST_GAMEFIELD = 201
    DRAW_REQUEST_GAMEREMOVEBLOCK = 202

    def __init__(self):
        self.state = App.SCENE_TITLE_INIT
        self.dreq = []

        self.field = None
        self.seeker = Seeker()

        self.click_position_x = None
        self.click_position_y = None
        self.remove_counter_start_time = 0

        pyxel.init(160, 120)
        pyxel.mouse(True)
        pyxel.run(self.update, self.draw)

    def update(self):
        dreq = []
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        if self.state == App.SCENE_TITLE_INIT:
            dreq.append(App.DRAW_REQUEST_TITLECLEARSCREEN)
            dreq.append(App.DRAW_REQUEST_TITLESTRING)

            self.state = App.SCENE_TITLE_LOOP

        elif self.state == App.SCENE_TITLE_LOOP:
            dreq.append(App.DRAW_REQUEST_TITLECLEARSCREEN)
            dreq.append(App.DRAW_REQUEST_TITLESTRING)
            dreq.append(App.DRAW_REQUEST_TITLEPUSHSTART)

            if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
                self.state = App.SCENE_TITLE_END

        elif self.state == App.SCENE_TITLE_END:
            self.field = Field()

            self.state = App.SCENE_GAME_INIT

        elif self.state == App.SCENE_GAME_INIT:
            self.click_position_x = None
            self.click_position_y = None

            self.remove_counter_start_time = 0

            self.seeker.seek(self.field)

            self.state = App.SCENE_GAME_LOOP

        elif self.state == App.SCENE_GAME_LOOP:
            dreq.append(App.DRAW_REQUEST_GAMECLEARSCREEN)
            dreq.append(App.DRAW_REQUEST_GAMEFIELD)

            if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
                self.click_position_x = pyxel.mouse_x
                self.click_position_y = pyxel.mouse_y
                self.state = App.SCENE_GAME_CLICK

        elif self.state == App.SCENE_GAME_CLICK:
            dreq.append(App.DRAW_REQUEST_GAMECLEARSCREEN)
            dreq.append(App.DRAW_REQUEST_GAMEFIELD)

            if self.click_position_x is not None and self.click_position_y is not None:
                posx = int((self.click_position_x - 10) / 10)
                posy = int((self.click_position_y - 10) / 10)
                print(posx, posy)
                self.field.field[posy][posx].on_click()
                self.state = App.SCENE_GAME_REMOVE

        elif self.state == App.SCENE_GAME_REMOVE:
            dreq.append(App.DRAW_REQUEST_GAMECLEARSCREEN)
            dreq.append(App.DRAW_REQUEST_GAMEREMOVEBLOCK)

            self.remove_counter_start_time = int(time.time())

            self.state = App.SCENE_GAME_REMOVE_LOOP

        elif self.state == App.SCENE_GAME_REMOVE_LOOP:
            dreq.append(App.DRAW_REQUEST_GAMECLEARSCREEN)
            dreq.append(App.DRAW_REQUEST_GAMEREMOVEBLOCK)

            print(time.time(), self.remove_counter_start_time)
            if int(time.time()) - self.remove_counter_start_time >= 1:
                self.state = App.SCENE_GAME_ALLDOWN_INIT

        elif self.state == App.SCENE_GAME_ALLDOWN_INIT:
            self.seeker.falldown(self.field)

            self.state = App.SCENE_GAME_ALLDOWN_LOOP

        elif self.state == App.SCENE_GAME_ALLDOWN_LOOP:
            self.state = App.SCENE_GAME_ALLDOWN_END
        elif self.state == App.SCENE_GAME_ALLDOWN_END:
            self.state = App.SCENE_GAME_SPWAN
        elif self.state == App.SCENE_GAME_SPWAN:
            dreq.append(App.DRAW_REQUEST_GAMECLEARSCREEN)
            dreq.append(App.DRAW_REQUEST_GAMEFIELD)

            self.seeker.spawn(self.field)

            self.state = App.SCENE_GAME_INIT

        elif self.state == App.SCENE_GAME_END:
            self.state = App.SCENE_GAME_END

        self.dreq = dreq

    def draw(self):
        dreq = list(self.dreq)

        for r in dreq:
            # タイトル画面のクリア
            if r == App.DRAW_REQUEST_TITLECLEARSCREEN:
                pyxel.cls(0)

            # タイトル
            elif r == App.DRAW_REQUEST_TITLESTRING:
                m = "SAMEGAME"
                pyxel.text(
                    (pyxel.width - len(m) * 4) / 2
                    , pyxel.height / 2 - pyxel.height / 6
                    , m
                    , 7)

            # プッシュスタート
            elif r == App.DRAW_REQUEST_TITLEPUSHSTART:
                m = "PUSH MOUSE L BUTTON"
                pyxel.text(
                    (pyxel.width - len(m) * 4) / 2
                    , pyxel.height / 2 + pyxel.height / 6
                    , m
                    , pyxel.frame_count % 16)

            # フィールド
            elif r == App.DRAW_REQUEST_GAMEFIELD:
                if self.field is not None:
                    for y in range(len(self.field.field)):
                        for x in range(len(self.field.field[y])):
                            c = self.field.field[y][x].color + 2
                            if self.field.field[y][x].state == 1:
                                c = 0
                            pyxel.rect(10 + (x * 10), 10 + (y * 10), 20 + (x * 10), 20 + (y * 10), c)

            # ゲーム画面のクリア
            elif r == App.DRAW_REQUEST_GAMECLEARSCREEN:
                pyxel.cls(15)

            # フィールドのブロック削除
            elif r == App.DRAW_REQUEST_GAMEREMOVEBLOCK:
                if self.field is not None:
                    for y in range(len(self.field.field)):
                        for x in range(len(self.field.field[y])):
                            c = self.field.field[y][x].color + 2
                            if self.field.field[y][x].state == 1:
                                c = 0
                            pyxel.rect(10 + (x * 10), 10 + (y * 10), 20 + (x * 10), 20 + (y * 10), c)


class Block:
    DIR_LEFT = 0
    DIR_RIGHT = 1
    DIR_TOP = 2
    DIR_BOTTOM = 3

    STATE_ALIVE = 0
    STATE_DIE = 1

    def __init__(self):
        self.color = random.randint(1, 5)
        self.state = Block.STATE_ALIVE
        self.touch = [None, None, None, None]

    def on_click(self):
        self.state = Block.STATE_DIE
        for t in self.touch:
            if t is not None and t.state == Block.STATE_ALIVE:
                t.on_click()


class Field:
    WIDTH = 14
    HEIGHT = 10

    def __init__(self):
        self.field = []
        for i in range(Field.HEIGHT):
            l = []
            for j in range(Field.WIDTH):
                l.append(Block())
            self.field.append(l)


class Seeker:
    def seek(self, field: Field):
        for y in range(len(field.field)):
            for x in range(len(field.field[y])):
                print(field.field[y][x].color, end="")
                if x > 0:
                    if field.field[y][x].color == field.field[y][x - 1].color:
                        field.field[y][x].touch[Block.DIR_LEFT] = field.field[y][x - 1]
                        print("l", end="")
                    else:
                        field.field[y][x].touch[Block.DIR_LEFT] = None

                if x < len(field.field[y]) - 1:
                    if field.field[y][x].color == field.field[y][x + 1].color:
                        field.field[y][x].touch[Block.DIR_RIGHT] = field.field[y][x + 1]
                        print("r", end="")
                    else:
                        field.field[y][x].touch[Block.DIR_RIGHT] = None

                if y > 0:
                    if field.field[y][x].color == field.field[y - 1][x].color:
                        field.field[y][x].touch[Block.DIR_TOP] = field.field[y - 1][x]
                        print("t", end="")
                    else:
                        field.field[y][x].touch[Block.DIR_TOP] = None

                if y < len(field.field) - 1:
                    if field.field[y][x].color == field.field[y + 1][x].color:
                        field.field[y][x].touch[Block.DIR_BOTTOM] = field.field[y + 1][x]
                        print("b", end="")
                    else:
                        field.field[y][x].touch[Block.DIR_BOTTOM] = None
                print("\t", end="")
            print("")

    def falldown(self, field: Field):
        temp = list(field.field)
        count = [0] * len(temp[0])
        for y in range(len(temp)):
            yy = len(temp) - 1 - y
            for x in range(len(temp[y])):
                if yy < len(temp):
                    if temp[yy + count[x]][x].state == 1:
                        self._bubbleup(field, x, yy + count[x])
                        count[x] += 1
        field.field = temp

    def _bubbleup(self, field: Field, x, y):
        for i in range(y):
            j = y - i
            if j > 0:
                t = field.field[j - 1][x]
                field.field[j - 1][x] = field.field[j][x]
                field.field[j][x] = t

    def spawn(self, field: Field):
        for y in range(len(field.field)):
            for x in range(len(field.field[y])):
                if field.field[y][x].state == 1:
                    field.field[y][x] = Block()


App()
