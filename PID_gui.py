import kivy
import asyncio
import nest_asyncio
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from pid import *

kivy.require('1.9.1')
nest_asyncio.apply()
Window.size = (300, 120)

class TelaLogin(GridLayout):
    def __init__(self, **kwargs):
        super(TelaLogin, self).__init__(**kwargs)
        self.cols = 2
        self.add_widget(Label(text='Kp'))
        self.Kp = TextInput(multiline=False, input_filter='float', hint_text='1')
        self.add_widget(self.Kp)
        self.add_widget(Label(text='Ki'))
        self.Ki = TextInput(multiline=False, input_filter='float', hint_text='0')
        self.add_widget(self.Ki)
        self.add_widget(Label(text='Kd'))
        self.Kd = TextInput(multiline=False, input_filter='float', hint_text='0')
        self.add_widget(self.Kd)
        self.bt = Button(text='Update')
        self.bt.bind(on_press=self.update)
        self.add_widget(self.bt)
        self.started = 0
        self.controller = None
        self.rc = None

    def update(self, instance):
        print('Updating gains...')
        if not self.started:
            self.controller = PID(T=0.1, order=2, Kp=float(self.Kp.text), Ki=float(self.Ki.text), Kd=float(self.Kd.text))
            self.rc = RemoteControl(self.controller)
            task = loop.create_task(self.rc.run())
            loop.run_until_complete(task)
            self.started = 1
        else:
            self.controller.update_gains(Kp=float(self.Kp.text), Ki=float(self.Ki.text), Kd=float(self.Kd.text))

class MyApp(App):
    def build(self):
        self.title = 'iDynamic PID'
        return TelaLogin()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MyApp().async_run(async_lib='asyncio'))
    loop.stop()
    loop.close()