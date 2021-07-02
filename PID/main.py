import kivy
import asyncio
import nest_asyncio
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from pid import *

kivy.require('1.9.1')
nest_asyncio.apply()
Window.size = (300, 200)

class TelaLogin(GridLayout):
    def __init__(self, **kwargs):
        super(TelaLogin, self).__init__(**kwargs)
        self.cols = 1
        self.started = 0
        self.controller = None

        self.setpoint_box = BoxLayout()
        self.setpoint_box.add_widget(Label(text='Set Point'))
        self.ref = TextInput(multiline=False, input_filter='float')
        self.setpoint_box.add_widget(self.ref)
        self.add_widget(self.setpoint_box)

        self.change_ref = Button(text='Set')
        self.change_ref.bind(on_press=self.update_sp)
        self.add_widget(self.change_ref)

        self.kp_box = BoxLayout()
        self.kp_box.add_widget(Label(text='Kp'))
        self.Kp = TextInput(multiline=False, input_filter='float')
        self.kp_box.add_widget(self.Kp)
        self.add_widget(self.kp_box)

        self.ki_box = BoxLayout()
        self.ki_box.add_widget(Label(text='Ki'))
        self.Ki = TextInput(multiline=False, input_filter='float')
        self.ki_box.add_widget(self.Ki)
        self.add_widget(self.ki_box)

        self.kd_box = BoxLayout()
        self.kd_box.add_widget(Label(text='Kd'))
        self.Kd = TextInput(multiline=False, input_filter='float')
        self.kd_box.add_widget(self.Kd)
        self.add_widget(self.kd_box)

        self.update = Button(text='Start Server')
        self.update.bind(on_press=self.update_PID)
        self.add_widget(self.update)
        '''
        self.stop = Button(text='Stop', background_color=[1,0,0,1])
        self.stop.bind(on_press=self.stop_sim)
        self.add_widget(self.stop)
        '''

    def update_sp(self, instance):
        self.controller.update_setpoint(float(self.ref.text))

    def update_PID(self, instance):
        if not self.started:
            self.controller = PID(T=0.1, order=2, Kp=float(self.Kp.text), Ki=float(self.Ki.text), Kd=float(self.Kd.text))
            rc = RemoteControl(self.controller)
            self.task = asyncio.create_task(rc.run())
            asyncio.get_running_loop().run_until_complete(self.task)
            self.update.text = 'Update'
            self.started = 1
        else:
            print('Updating gains...')
            self.controller.update_gains(Kp=float(self.Kp.text), Ki=float(self.Ki.text), Kd=float(self.Kd.text))
'''
    def stop_sim(self, instance):
        print("cancelando essa bagaça")
        self.task.cancel()
        self.started = 0
'''
class MyApp(App):
    def build(self):
        self.title = 'iDynamic PID'
        return TelaLogin()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MyApp().async_run(async_lib='asyncio'))
    loop.stop()
    loop.close()
