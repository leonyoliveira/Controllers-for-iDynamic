import kivy
import asyncio
from kivy.core.text import markup
import nest_asyncio
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from ladrc import *

kivy.require('1.9.1')
nest_asyncio.apply()
Window.size = (300, 200)

class TelaLogin(GridLayout):
    def __init__(self, **kwargs):
        super(TelaLogin, self).__init__(**kwargs)
        self.cols = 2
        self.add_widget(Label(text='Order'))
        self.order = TextInput(multiline=False, input_filter='float', hint_text='1')
        self.add_widget(self.order)
        self.add_widget(Label(text='b[sub]0[/sub]', markup=True))
        self.b0 = TextInput(multiline=False, input_filter='float', hint_text='1')
        self.add_widget(self.b0)
        self.add_widget(Label(text='s[sub]CL[/sub]', markup=True))
        self.s_cl = TextInput(multiline=False, input_filter='float', hint_text='1')
        self.add_widget(self.s_cl)
        self.add_widget(Label(text='s[sub]ESO[/sub]', markup=True))
        self.s_eso = TextInput(multiline=False, input_filter='float', hint_text='3')
        self.add_widget(self.s_eso)
        self.add_widget(Label(text='R'))
        self.R = TextInput(multiline=False, input_filter='float', hint_text='5')
        self.add_widget(self.R)
        self.bt = Button(text='Update')
        self.bt.bind(on_press=self.update)
        self.add_widget(self.bt)
        self.started = 0
        self.controller = None
        self.rc = None

    def update(self, instance):
        print('Updating parameters...')
        if not self.started:
            self.controller = LADRC(T=0.1, order=int(self.order.text), s_cl=float(self.s_cl.text), s_eso=float(self.s_eso.text), b0=float(self.b0.text), R=float(self.R.text))
            self.rc = RemoteControl(self.controller)
            task = loop.create_task(self.rc.run())
            loop.run_until_complete(task)
            self.started = 1
        else:
            self.controller.update_LADRC(order=int(self.order.text), s_cl=float(self.s_cl.text), s_eso=float(self.s_eso.text), b0=float(self.b0.text), R=float(self.R.text))

class MyApp(App):
    def build(self):
        self.title = 'iDynamic LADRC'
        return TelaLogin()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MyApp().async_run(async_lib='asyncio'))
    loop.stop()
    loop.close()