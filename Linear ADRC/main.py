import kivy
import asyncio
from kivy.core.text import markup
from matplotlib.pyplot import text
import nest_asyncio
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from ladrc import *

kivy.require('1.9.1')
nest_asyncio.apply()
Window.size = (300, 250)

class TelaLogin(GridLayout):
    def __init__(self, **kwargs):
        super(TelaLogin, self).__init__(**kwargs)
        self.cols = 1
        self.started = 0
        self.controller = None
        self.rc = None

        self.setpoint_box = BoxLayout()
        self.setpoint_box.add_widget(Label(text='Set Point'))
        self.ref = TextInput(multiline=False, input_filter='float')
        self.setpoint_box.add_widget(self.ref)
        self.add_widget(self.setpoint_box)

        self.change_ref = Button(text='Set')
        self.change_ref.bind(on_press=self.update_sp)
        self.add_widget(self.change_ref)

        self.order_box = BoxLayout()
        self.order_box.add_widget(Label(text='Order'))
        self.order = TextInput(multiline=False, input_filter='float')
        self.order_box.add_widget(self.order)
        self.add_widget(self.order_box)

        self.b0_box = BoxLayout()
        self.b0_box.add_widget(Label(text='b[sub]0[/sub]', markup=True))
        self.b0 = TextInput(multiline=False, input_filter='float')
        self.b0_box.add_widget(self.b0)
        self.add_widget(self.b0_box)

        self.s_cl_box = BoxLayout()
        self.s_cl_box.add_widget(Label(text='s[sub]CL[/sub]', markup=True))
        self.s_cl = TextInput(multiline=False, input_filter='float')
        self.s_cl_box.add_widget(self.s_cl)
        self.add_widget(self.s_cl_box)

        self.s_eso_box = BoxLayout()
        self.s_eso_box.add_widget(Label(text='s[sub]ESO[/sub]', markup=True))
        self.s_eso = TextInput(multiline=False, input_filter='float')
        self.s_eso_box.add_widget(self.s_eso)
        self.add_widget(self.s_eso_box)

        self.R_box = BoxLayout()
        self.R_box.add_widget(Label(text='R'))
        self.R = TextInput(multiline=False, input_filter='float')
        self.R_box.add_widget(self.R)
        self.add_widget(self.R_box)

        self.update = Button(text='Start Server')
        self.update.bind(on_press=self.update_LADRC)
        self.add_widget(self.update)
    
    def update_sp(self, instance):
        self.controller.update_setpoint(float(self.ref.text))

    def update_LADRC(self, instance):
        if not self.started:
            self.controller = LADRC(T=0.1, order=int(self.order.text), s_cl=float(self.s_cl.text), s_eso=float(self.s_eso.text), b0=float(self.b0.text), R=float(self.R.text))
            self.rc = RemoteControl(self.controller)
            task = loop.create_task(self.rc.run())
            loop.run_until_complete(task)
            self.update.text = 'Update'
            self.started = 1
        else:
            print('Updating parameters...')
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
