import kivy

kivy.require("2.0.0")

from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.screen import Screen
from kivy.properties import ObjectProperty, StringProperty

from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.gridlayout import GridLayout
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.toolbar import MDToolbar


class Card(MDCard):
    title = StringProperty()
    description = StringProperty(">_>")

    def __init__(self, title, **kwargs):
        super(Card, self).__init__(**kwargs)
        self.title = title


class MainGrid(GridLayout):
    def __init__(self, **kwargs):
        super(MainGrid, self).__init__(**kwargs)

        self.cols = 3
        self.pos_hint = {"center_x": 0.5, "center_y": 0.3}
        self.spacing = [10, 100]
        self.padding = [10, 10, 10, 10]

        self.add_widget(Card(title="Hello World"))
        self.add_widget(Card(title="Hello World"))
        self.add_widget(Card(title="Hello World"))
        self.add_widget(Card(title="Hello World"))
        self.add_widget(Card(title="Hello World"))
        self.add_widget(Card(title="Hello World"))


class ContentNavigationDrawer(MDBoxLayout):
    screen_manager = ObjectProperty()
    nav_drawer = ObjectProperty()


class SideBar(MDToolbar):
    pass


class ClsRoomScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.add_widget(MainGrid())


class FrontApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        screen_manager = ScreenManager()
        nav_screen = Screen()
        nav_screen.add_widget(ClsRoomScreen())
        screen_manager.add_widget(nav_screen)
        return screen_manager


if __name__ == "__main__":
    FrontApp().run()
