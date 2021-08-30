import kivy
from kivy.uix.boxlayout import BoxLayout

kivy.require("2.0.0")

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.properties import ObjectProperty, StringProperty

from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.screen import MDScreen
from kivymd.uix.gridlayout import GridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDToolbar

from client import Client
import threading
import time
from functools import partial

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


class ClsRoomScreen(MDScreen):
    def __init__(self, data, **kw):
        super().__init__(**kw)
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
