from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.scatter import Scatter
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ReferenceListProperty, BooleanProperty
from kivy.vector import Vector
from kivy.clock import Clock
from math import sqrt
from kivy.graphics import Line
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics.instructions import InstructionGroup
from kivy.uix.settings import SettingsWithSidebar
from settingsjson import settings_json
from kivy.core.image import Image
from random import choice

import os
import math

class Planet(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    red = NumericProperty(255)
    green = NumericProperty(255)
    blue = NumericProperty(255)
    colour = ReferenceListProperty(red, green, blue)

    fixed = BooleanProperty(False)

    mass = NumericProperty(1)
    density = NumericProperty(10)

    showforcelimit = NumericProperty(5)

    def __init__(self, fixed, position, velocity, mass, density, colour,
                 **kwargs):
        super(Planet, self).__init__(**kwargs)
        self.fixed = fixed
        self.mass = mass
        self.center = (position[0],position[1])
        self.velocity = velocity
        self.density = density
        self.colour = colour
        self.showforcelimit = float(App.get_running_app().config.get('planetapp',
                                                                     'showforcelimit'))
        self.calc_size()
        self.hillbodies = []

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

    def calc_gravity(self, planet, gravity):
        if not self.fixed:
            dist_x = self.center_x - planet.center_x
            dist_y = self.center_y - planet.center_y
            dist = self.parent.calc_distance(self.center,planet.center)

            force = (gravity * self.mass * planet.mass) / (dist**2)
            force_x = force * (dist_x / dist)
            force_y = force * (dist_y / dist)

            self.calc_hillbodies(force, planet)

            self.velocity_x -= force_x / self.mass
            self.velocity_y -= force_y / self.mass

    def calc_hillbodies(self, force, planet):
        # typecasting problem while crosscompiling
        foo = App.get_running_app().config.get('planetapp','showforcemode')
        if foo == u'0':
            return
        if ((force / self.mass) > (self.showforcelimit * 0.0002)):
            if not planet.fixed:
                if not planet in self.hillbodies: 
                    self.hillbodies.append(planet)
        else:
            if planet in self.hillbodies:
                self.hillbodies.remove(planet)

        for dude in self.canvas.children:
            if 'InstructionGroup' in  type(dude).__name__:
                self.canvas.remove(dude)
        shit = InstructionGroup()
        for body in self.hillbodies:
            shit.add(Line(points=(self.center_x,self.center_y,
                                  body.center_x,body.center_y),
                          width=1,
                          group=str(self.uid)))
        if len(self.hillbodies) > 0:
            self.canvas.add(shit)


    def merge(self, planet):

        impulse_x = (self.velocity_x * self.mass + planet.velocity_x * planet.mass)
        impulse_y = (self.velocity_y * self.mass + planet.velocity_y * planet.mass)

        self.mass += planet.mass

        if not self.fixed:
            self.velocity_x = impulse_x / self.mass
            self.velocity_y = impulse_y / self.mass
        if (self.red > 0.1) and not self.fixed:
            self.red -= 0.1
        self.hillbodies = []

    def on_mass(self, instance, value):
        self.calc_size()

    def calc_size(self):
        diameter = 2 * sqrt(self.density * self.mass / 3.14)
        self.size = (diameter,diameter)

class PlanetGame(Scatter):
    zoom = NumericProperty(1)
    gravity = NumericProperty(1)
    planetmass = NumericProperty(1)
    resetmass = NumericProperty(10)
    sunmass = NumericProperty(1000)

    def __init__(self, **kwargs):
        super(PlanetGame, self).__init__(**kwargs)
        self.textures = []
        self.files = []
        self.load_textures()

    def i_am_dead(self, deadplanet):
        for planet in self.children:
            if deadplanet in planet.hillbodies:
                planet.hillbodies.remove(deadplanet)

    def load_textures(self):
        path = ('./textures/')
        for file in os.listdir(path):
            if file.endswith('.png'):
                self.files.append(path + str(file))
        for string in self.files:
            self.textures.append(Image(string).texture)

    def add_planet(self, fixed, position, velocity, mass=1, 
                   density=5, colour=(1,1,1)):
        new_planet = Planet(fixed, position, velocity, mass, density, colour)
        if not fixed:
            new_planet.canvas.children[1].texture = choice(self.textures)
        self.add_widget(new_planet)

    def update(self,dt):
        for planet in self.children:
            if planet.fixed:
                planet.center = (self.width/2+50,self.height/2)
            planet.move()
            for planet2 in self.children:
                if planet == planet2:
                    continue
                planet.calc_gravity(planet2, self.gravity)
                if not planet.collide_widget(planet2):
                    continue
                if planet.mass < planet2.mass:
                    continue
                planet.merge(planet2)
                self.i_am_dead(planet2)
                self.remove_widget(planet2)

    def on_touch_down(self, touch):
        touch.push()
        touch.apply_transform_2d(self.to_local)

        ud = touch.ud
        ud['id'] = 'gametouch'
        ud['firstpos'] = touch.pos
        ud['group'] = g = str(touch.uid)

        with self.canvas:
            ud['lines'] = [
                Line(points=(touch.x,touch.y,touch.x+1,touch.y+1),width=1,
                     group=g)]
        
        touch.grab(self)
        touch.pop()

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return
        touch.push()
        touch.apply_transform_2d(self.to_local)
        ud = touch.ud

        velocity = ((ud['firstpos'][0] - touch.x) / -50, (ud['firstpos'][1] - touch.y) / - 50)
        planetpos = (ud['firstpos'][0], ud['firstpos'][1])

        sunpos = (self.width/2+50,self.height/2)
        trajectory = self.calc_trajectory(planetpos, velocity, self.planetmass,
                                          sunpos, self.sunmass, 1, 250)  

        # make this optional!
        #ud['lines'][0].points = (ud['firstpos'][0],ud['firstpos'][1],
        #                         touch.x,touch.y)


        ud['lines'][0].points = trajectory




        touch.pop()

    def calc_trajectory (self, coord_planet, speed_planet, weight_planet, coord_sun,
                     weight_sun, interval, count):
	gamma =  self.gravity
	L = []
	
	coords = coord_planet
	speed = speed_planet
	for i in range(count):
		r = self.calc_distance(coords, coord_sun)
		g = (-1 * gamma) * (weight_sun) / math.pow(r, 2.0) 
		gx = g * ((coords[0] - coord_sun[0]) / r)
		gy = g * ((coords[1] - coord_sun[1]) / r)
		speed = (speed[0] + (gx * interval), speed[1] + (gy * interval))
		coords = (coords[0] + (speed[0] * interval) + 
                          (0.5 * gx * math.pow(interval, 2.0)),
                          coords[1] + (speed[1] * interval) + 
                          (0.5 * gy * math.pow(interval, 2.0)))
		
		L.append(coords)
	
        R = []
        for item in L:
            R.append(item[0])
            R.append(item[1])

        return tuple(R)

    def calc_distance(self, tuple1, tuple2):
        dist =  math.sqrt(math.pow(tuple1[0] - tuple2[0], 2.0) + 
                          math.pow(tuple1[1] - tuple2[1], 2.0))
        if dist == 0: 
            dist = 0.000001
        return dist	 

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return
        touch.ungrab(self)
        touch.push()
        touch.apply_transform_2d(self.to_local)

        ud = touch.ud

        touchdownv = Vector(ud['firstpos'])
        touchupv = Vector(touch.pos)
        velocity = (touchupv - touchdownv) / 50
        print '#'
        print velocity

        self.add_planet(False, ud['firstpos'], (velocity.x, velocity.y), self.planetmass)
        self.canvas.remove_group(ud['group'])

        touch.pop()

    def on_zoom(self,instance,value):
        self.scale = 1/value

    def clear_planets(self):
        L = []
        for planet in self.children:
            if planet.mass < self.resetmass:
                L.append(planet)
        if L:
            for planet in L:
                self.i_am_dead(planet)
            self.clear_widgets(L)

    def reset_game(self):
        L = []
        for planet in self.children:
            L.append(planet)
        if L:
            self.clear_widgets(L)
        sunmass = float(App.get_running_app().config.get('planetapp','defaultsunmass'))
        self.sunmass = sunmass
        self.gravity = float(App.get_running_app().config.get('planetapp','gravity'))
        self.planetmass = float(App.get_running_app().config.get('planetapp','planetmass'))
        self.resetmass = float(App.get_running_app().config.get('planetapp','resetmass'))
        self.add_planet(True, (100,100), (0,0), float(sunmass), 10, (1,1,1))

class PlanetGameLayout(BoxLayout):
    def on_touch_down(self, touch):
        if self.children[0].collide_point(touch.x,touch.y):
            self.children[0].on_touch_down(touch)
            #print 'Button1'
        elif self.children[1].collide_point(touch.x,touch.y):
            self.children[1].on_touch_down(touch)
            #print 'Button2'
        elif self.children[3].collide_point(touch.x,touch.y):
            self.children[3].on_touch_down(touch)
            #print 'Slider'
        else:
            self.children[2].on_touch_down(touch)
            #print 'Game'

    def on_touch_up(self, touch):
        if self.children[0].collide_point(touch.x,touch.y):
            self.children[0].on_touch_up(touch)
            #print 'Button1'
        elif self.children[1].collide_point(touch.x,touch.y):
            self.children[1].on_touch_up(touch)
            #print 'Button2'
        elif self.children[3].collide_point(touch.x,touch.y):
            self.children[3].on_touch_up(touch)
            #print 'Slider'
        else:
            pass
            #self.children[2].on_touch_up(touch)
            #print 'Game'


    def clear_planets(self,instance):
        self.children[2].clear_planets()

    def reset_game(self):
        self.children[2].reset_game()

class SettingsButton(Button):
    pass


class PlanetApp(App):
    def build(self):

        self.settings_cls = SettingsWithSidebar

        game = PlanetGame(do_rotation=False,do_translation=False)
        # Settings come in as unicode!
        sunmass = float(App.get_running_app().config.get('planetapp','defaultsunmass'))
        game.sunmass = sunmass
        game.gravity = float(App.get_running_app().config.get('planetapp','gravity'))
        game.planetmass = float(App.get_running_app().config.get('planetapp','planetmass'))
        game.resetmass = float(App.get_running_app().config.get('planetapp','resetmass'))
        game.add_planet(True, (100,100), (0,0), sunmass, 10, (1,1,1))
        
        Clock.schedule_interval(game.update, 1.0 / 120.0)

        self.root = PlanetGameLayout()
        self.root.add_widget(game)

        b = Button(text="Reset",size_hint=(.1,.1))
        b.bind(on_press=self.root.clear_planets)
        self.root.add_widget(b)
        b2 = SettingsButton(text="Settings",size_hint=(.1,.1))
        self.root.add_widget(b2)


    def build_config(self, config):
        config.setdefaults('planetapp', {
            'defaultsunmass': 1000,
            'gravity' : 2,
            'resetmass' : 50,
            'showforcemode' : False,
            'showforcelimit' : 5,
            'planetmass' : 10}),
        '''
            'boolexample': True,
            'optionsexample': 'option2',
            'stringexample': 'some_string',
            'pathexample': '/some/path'})
        '''

    def build_settings(self, settings):
        settings.add_json_panel('PlanetApp',
                                self.config,
                                data=settings_json)

    def on_config_change(self, config, section,
                         key, value):
        print config, section, key, value
        self.root.reset_game()

if __name__ == '__main__':
    PlanetApp().run()
