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
# This will help to run the GUI parallel with websocket server
nest_asyncio.apply()

# Setting window width and height
Window.size = (250, 280)

class TelaLogin(GridLayout):
    # This class will create the main screen of the GUI.

    def __init__(self, **kwargs):
        super(TelaLogin, self).__init__(**kwargs)
        
        '''
        We'll define cols = 1 so all elements will be place below one another.
        Variable 'started' will indicate if the server was already started or not. (Stop server function not working propertly yet.)
        'controller' and 'rc' will instantiate the objects from ControlLib classses.
        The following blocks of code will instantiate the objects needed to change set point values and ADRC parameters, adding the widgets to the main screen.
        For each ADRC parameter, there'll be container with its label and a input box to change its value.
        'Set' button is added to change reference value on pressed; 'Start/Update Server' change the controller values and starts the server, if it still not started;
            'Stop Server' will stop the websocket server code (Not working yet).
        '''

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

        self.stop = Button(text='Stop Server', background_color=[1,0,0,1])
        self.stop.bind(on_press=self.stop_sim)
        self.add_widget(self.stop)
    
    def update_sp(self, instance):
        # This function will be called when 'Set' button is pressed, changing set point value.
        self.controller.update_setpoint(float(self.ref.text))

    def stop_sim(self, instance):
        # This function will be called when 'Stop Server' button is pressed, stopping server from running. (Not working propertly yet)
        self.controller.stop_press()
        self.update.text = 'Start Server'
        self.started = 0

    def update_LADRC(self, instance):
        # This function will be called when 'Stop Server' button is pressed
        if not self.started:
            # If server isn't running yet, it creates a new instance of ADRC, and runs the server on a task.
            self.controller = LADRC(T=0.1, order=3, adrc_order=int(self.order.text), s_cl=float(self.s_cl.text), s_eso=float(self.s_eso.text), b0=float(self.b0.text), R=float(self.R.text))
            self.rc = RemoteControl(self.controller)
            task = loop.create_task(self.rc.run())
            loop.run_until_complete(task)
            self.update.text = 'Update Parameters'
            self.started = 1
        else:
            # If server is already running, this will only update ADRC parameters.
            print('Updating parameters...')
            self.controller.update_LADRC(adrc_order=int(self.order.text), s_cl=float(self.s_cl.text), s_eso=float(self.s_eso.text), b0=float(self.b0.text), R=float(self.R.text))

class MyApp(App):
    '''
    This class will instantiate an kivy App, containing an object of TelaLogin class.
    '''
    def build(self):
        self.title = 'iDynamic LADRC'
        return TelaLogin()

if __name__ == '__main__':
    # The 'MyApp' object is started inside an asyncio loop, so it can be executed along the websocket server, asynchronously.
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MyApp().async_run(async_lib='asyncio'))
    loop.stop()
    loop.close()
