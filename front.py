from kivy.app import App

# from kivy.uix.label import Label
# from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivymd.app import MDApp


class MainGrid(GridLayout):
    def __init__(self, **kwargs):
        super(MainGrid, self).__init__(**kwargs)
        self.cols = 2
        self.add_widget(Label(text="Hello World"))
        self.add_widget(Label(text="Hello World"))


class FrontApp(App):
    def build(self):
        return Label(text="Hello World")


if __name__ == "__main__":
    FrontApp().run()
