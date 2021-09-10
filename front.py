import kivy
from kivy.uix.boxlayout import BoxLayout

kivy.require("2.0.0")

import os
import platform
import subprocess
import threading
import time
from functools import partial

from kivy.lang import Builder
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.scrollview import ScrollView
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import GridLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.list import ThreeLineListItem
from kivymd.uix.screen import MDScreen
from kivymd.uix.toolbar import MDToolbar
from tinydb import where

from client import Client


# TODO responsive grid layout
class Card(MDCard):
    title = StringProperty()
    description = StringProperty("Not found")

    def __init__(self, title, description, **kwargs):
        super(Card, self).__init__(**kwargs)
        self.title = title
        self.description = description


class MainGrid(ScrollView):
    grid = ObjectProperty(None)

    def __init__(self, data, **kwargs):
        super(MainGrid, self).__init__(**kwargs)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        # for i in client.course_db:
        #     self.grid.add_widget(Card(title=i["name"], description=i.get("section", "Not found")))
        self.grid.add_widget(Card(title="AAAAAA", description="AAAAAa"))
        self.grid.add_widget(Card(title="AAA\nAAA", description="AAAAAa"))
        self.grid.add_widget(Card(title="AAA\nAAA", description="AA\nAAAa"))


class SideBar(MDScreen):
    card_screen = ObjectProperty()
    screen_manager = ObjectProperty()

    def __init__(self, **kwargs):
        super(SideBar, self).__init__(**kwargs)
        self.ids.screen_manager.add_widget(ClsRoomScreen({}))
        self.ids.screen_manager.current = "Search"


class ItemTile(ThreeLineListItem):
    def open_file(self, path):
        filepath = client.data_path / path
        if platform.system() == "Darwin":  # macOS
            subprocess.call(("open", filepath))
        elif platform.system() == "Windows":  # Windows
            os.startfile(filepath)
        else:  # linux variants
            subprocess.call(("xdg-open", filepath))


class SearchScreen(MDScreen):
    def search(self):
        # print(*[i.values() for i in client.search(self.ids["search_text"].text)], sep="\n")
        self.ids.search_list.clear_widgets()
        for i in client.search(self.ids["search_text"].text):
            vals = i.values()
            if course := client.course_db.get(where("id") == vals[0]):
                course_name = course["name"] + " - " + course.get("section", "")
            else:
                course_name = "Course Not Found"
            self.ids.search_list.add_widget(
                ItemTile(
                    text=course_name,
                    secondary_text=vals[3],
                    tertiary_text=f"PageNo: {vals[2]}",
                )
            )


class ClsRoomScreen(MDScreen):
    def __init__(self, data, **kw):
        super().__init__(**kw)
        self.name = "Classroom"
        self.add_widget(MainGrid(data))


class FrontApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        # self.theme_cls.theme_style = "Dark"
        if not len(client.course_db) > 7:
            t1 = threading.Thread(target=client.load_courses, args=[])
            t1.start()
        return SideBar()


# Miscellaneous
class ContentNavigationDrawer(MDBoxLayout):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()


if __name__ == "__main__":
    # Get a better way instead of globals
    global client
    client = Client()
    # client.auth()
    FrontApp().run()
