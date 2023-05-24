from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty, ListProperty, NumericProperty, BooleanProperty, ObjectProperty
from kivy.core.window import Window
import functions as fun
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.config import Config
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.dropdown import DropDown
from kivy_garden.graph import Graph, BarPlot
from kivy.graphics import Rectangle, Color, RoundedRectangle, Line
from kivy.graphics.texture import Texture
from random import shuffle, randint
from kivy.animation import Animation
from kivy.uix.screenmanager import FallOutTransition, NoTransition
from itertools import chain
import os
import sys
import platform
from kivy.utils import platform as pltfrm
from kivy.resources import resource_add_path, resource_find



if pltfrm == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE] )
    from android.storage import primary_external_storage_path
    primary_ext_storage = primary_external_storage_path()
else:
    primary_ext_storage ="/"

if platform.system() == "Windows":
    Config.set('graphics', 'width', '270')
    Config.set('graphics', 'height', '600')
    Config.set('graphics', 'borderless', '0')
    Config.set('kivy', 'window_icon', 'Images\icon_background.ico')
    pass

volume = 1
reviewqueue = fun.get_all_reviews()
level, levelname = fun.get_current_level()
lessonqueue = fun.getlessonqueue(level)


def updatequeues():
    global reviewqueue
    global lessonqueue
    global level
    reviewqueue = fun.get_all_reviews()
    lessonqueue = []
    for j in range(5):
        lessonqueue += fun.getlessonqueue(j)
    level, levelname = fun.get_current_level()


def create_gradient(*args, horizontal=False):
    if horizontal is False:
        size = (len(args), 1)
    elif horizontal is True:
        size = (1, len(args))
    texture = Texture.create(size=size, colorfmt='rgba')
    buf = bytes([int(v * 255) for v in chain(*args)])  # flattens
    texture.blit_buffer(buf, colorfmt='rgba', bufferfmt='ubyte')
    return texture


class ReviewScreen(Screen):
    answer = ObjectProperty(None)
    reviewqueuelabel = StringProperty()      # all sid of reviews ready
    emeaning = StringProperty()
    gmeaning = StringProperty()
    correctanswer = StringProperty()
    reviews = ListProperty()
    reviewcolor = ListProperty()
    givenanswer = StringProperty()
    correction = StringProperty()
    submitting = StringProperty()
    reviewqueue = StringProperty()
    windowsize = Window.size
    widgetstodelete = []

    def __init__(self, **kwargs):
        super(ReviewScreen, self).__init__(**kwargs)
        self.reviewcolor = [1, 1, 1, 1]
        Window.bind(on_key_down=self._on_key_down)

    def on_pre_enter(self, *args):
        self.reviewcolor = [1, 1, 1, 1]
        self.correction = ""
        self.givenanswer = ""
        self.reviewqueuelabel = str(len(reviewqueue))
        self.emeaning = "..."
        self.gmeaning = ""
        self.correctanswer = ""
        self.submitting = "Submit Answer"
        if len(reviewqueue) == 0:
            self.reviewqueue = "No Reviews"
        else:
            self.emeaning = reviewqueue[0][1]
        if self.widgetstodelete is not None:
            for i in self.widgetstodelete:
                self.ids.review_deletion_layout.remove_widget(i)
        self.review_availability()

    def on_enter(self, *args):
        self.ids.answer.focus = True
        if len(reviewqueue) == 0:
            Clock.schedule_once(self.add_canvas, 0.01)

    def on_leave(self, *args):
        if self.widgetstodelete is not None:
            for i in self.widgetstodelete:
                self.ids.review_deletion_layout.remove_widget(i)
        pass

    def review_availability(self):
        # if no reviews are up, the screen will be different and buttons will lead to new lessons or statistics
        if len(reviewqueue) != 0:
            self.ids.review_deletion_layout.padding = "0dp"
            self.ids.review_deletion_layout.spacing = "0dp"
            for j in self.ids.review_deletion_layout.children:
                fun.hide_widget(j, dohide=False)
        else:
            for i in self.ids.review_deletion_layout.children:
                fun.hide_widget(i, dohide=True)
            self.add_no_reviews()

    def add_no_reviews(self):
        # defining design if no reviews are available
        label = Label(
            text="Currently no reviews!",
            height="56dp",
            size_hint_y=None,
            color=(0, 0, 0, 1),
            background_normal='',
            background_color=(1, 1, 1, 0),
            halign='center',
            valign='center')
        but1 = Button(
            text="Learn new vocabulary in\n\n[b]Lesson section[/b]",
            markup=True,
            on_press=lambda x: self.change_screen(x, "lessonscreen"),
            height="72dp",
            size_hint_x=0.5,
            size_hint_y=None,
            color=(0, 0, 0, 1),
            background_normal='',
            background_color=(1, 1, 1, 0),
            halign='center',
            valign='center')
        but2 = Button(
            text="Check the review status in\n\n[b]Statistics menu[/b]",
            on_press=lambda x: self.change_screen(x, "StatisticsScreen"),
            markup=True,
            height="72dp",
            size_hint_y=None,
            color=(0, 0, 0, 1),
            background_normal='',
            background_color=(1, 1, 1, 0),
            halign='center',
            valign='center')
        # add widgets to existing gridlayout
        self.ids.review_deletion_layout.add_widget(label)
        self.ids.review_deletion_layout.add_widget(but1)
        self.ids.review_deletion_layout.add_widget(but2)
        self.ids.review_deletion_layout.padding = "8dp"
        self.ids.review_deletion_layout.spacing = "8dp"
        self.widgetstodelete.append(label)
        self.widgetstodelete.append(but1)
        self.widgetstodelete.append(but2)

    def add_canvas(self, *kwargs):
        # adding canvas to the buttons when no reviews are available
        for englishbutton in self.ids.review_deletion_layout.children:
            if isinstance(englishbutton, Button):
                englishbutton.canvas.before.add(Color(rgba=(0, 0, 0, 0.1)))
                englishbutton.canvas.before.add(RoundedRectangle(size=englishbutton.size, pos=englishbutton.pos,
                                                                 radius=[(englishbutton.size[1] + 100) * 0.1]))

    def change_screen(self, instance, screenname):
        # need extra function for buttons to change screen on press
        self.manager.current = screenname

    def do_one_review(self):
        # function to see if answer is correct and change screen accordingly
        if len(reviewqueue) != 0 and len(self.answer.text) > 0:
            self.correctanswer = fun.do_a_review(reviewqueue[0], self.answer.text)
            if self.correctanswer == "Wrong answer":
                self.sound = SoundLoader.load("Sound/correction/wrong-answer.wav")
                self.sound.volume = volume
                self.sound.play()
                science.currentreview = reviewqueue[0]
                self.reviewcolor = (250/255, 90/255, 70/255, 1)
                self.givenanswer = ": " + self.answer.text
                self.correction = reviewqueue[0][2]
                if reviewqueue[0][4] != " ":
                    self.correction += " oder " + reviewqueue[0][4]
                # add +1 to counter for wrong answer
                reviewqueue[0] = reviewqueue[0][:5] + ((reviewqueue[0][5]+1), (reviewqueue[0][6]+1))
                reviewqueue.insert(randint(0, len(reviewqueue)), (reviewqueue[0]))
                reviewqueue.pop(0)
                Clock.schedule_once(self.settonext, 0.05)
            elif self.correctanswer == "Correct answer":
                reviewqueue.pop(0)
                self.update_text()
                self.sound = SoundLoader.load("Sound/correction/correct-answer.wav")
                self.sound.volume = volume
                self.sound.play()
        else:
            pass

    def settonext(self, *kwargs):
        self.submitting = "Next"

    def resettext(self, _):
        self.answer.text = ""

    def update_text(self):
        # changing label names
        if len(reviewqueue) == 0:
            self.reviewqueuelabel = "No Reviews"
            self.emeaning = ""
        elif len(reviewqueue) > 0:
            self.reviewqueuelabel = str(len(reviewqueue))
            self.emeaning = reviewqueue[0][1]
        self.reviewcolor = (1, 1, 1, 1)
        self.givenanswer = ""
        self.correction = ""
        self.submitting = "Submit Answer"
        self.correctanswer = ""
        Clock.schedule_once(self.resettext)

    def _on_key_down(self, instance, keyboard, keycode, text, modifiers):
        # keyboard inputs
        if keycode == 40 and self.manager.current == "reviewscreen" and self.submitting == "Submit Answer":
            self.do_one_review()
            Clock.schedule_once(self.resettext)

        if keycode == 40 and self.manager.current == "reviewscreen" and self.submitting == "Next":
            self.update_text()

        if (keycode == 41 or keycode == 270) and self.manager.current != "mainscreen":
            self.manager.current = "mainscreen"

        elif (keycode == 41 or keycode == 270) and self.manager.current == "mainscreen":
            App.get_running_app().stop()
        pass


class LessonLearnScreen(Screen):
    emeaning = StringProperty()
    gmeaning = StringProperty()
    esynonym = StringProperty()
    gsynonym = StringProperty()
    levellength = NumericProperty()
    nextlessontext = StringProperty()
    level = StringProperty()
    definition = StringProperty()
    lessonnumber = NumericProperty()
    lessonquizqueue = ListProperty()
    windowsize = Window.size
    sound = ObjectProperty()
    levelfinished = []

    def __init__(self, **kwargs):
        super(LessonLearnScreen, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.lessonnumber = 0
        self.lessonquizqueue = lessonqueue[:5]
        self.nextlessontext = "Next Lesson"
        self.level = str(level)
        if len(self.lessonquizqueue) != 0:
            self.updatetext()
            self.levellength = len(self.lessonquizqueue)
            if self.levelfinished is not None:
                for i in self.levelfinished:
                    self.ids.deletion_layout.remove_widget(i)
            for i in self.ids.deletion_layout.children:
                fun.hide_widget(i, dohide=False)
        else:
            for i in self.ids.deletion_layout.children:
                fun.hide_widget(i, dohide=True)
            label = (Label(text=fun.levelfinishedtext(), height="144dp",
                             color=(0, 0, 0, 1), background_normal='', background_color=(1, 1, 1, 0),
                             halign='center', valign='center'))
            self.ids.deletion_layout.add_widget(label)
            self.levelfinished.append(label)
        Window.bind(on_key_down=self._on_keyboard_down)

    def updatetext(self):
        if self.sound is not None:
            self.sound.stop()
        self.emeaning = self.lessonquizqueue[self.lessonnumber][1]
        self.gmeaning = self.lessonquizqueue[self.lessonnumber][2]
        self.esynonym = self.lessonquizqueue[self.lessonnumber][3]
        self.gsynonym = self.lessonquizqueue[self.lessonnumber][4]
        self.definition = self.lessonquizqueue[self.lessonnumber][6]
        self.sound = SoundLoader.load(self.lessonquizqueue[self.lessonnumber][7])
        self.sound.volume = volume
        self.sound.play()

    def nextlesson(self):
        if self.lessonnumber < len(self.lessonquizqueue)-1 and self.lessonnumber < 4:
            self.lessonnumber += 1
            self.updatetext()
            if self.lessonnumber == self.levellength-1:
                self.nextlessontext = "Go to Quiz"

    def lastlesson(self):
        if self.lessonnumber > 0:
            self.lessonnumber -= 1
            self.updatetext()
            if self.lessonnumber < self.levellength-1:
                self.nextlessontext = "Next Lesson"

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 20 and self.manager.current == "lessonscreen":
            self.lastlesson()
        elif keycode == 8 and self.manager.current == "lessonscreen":
            if self.lessonnumber < self.levellength-1:
                self.nextlesson()
            else:
                self.manager.current = "lessonquizscreen"


class MainScreen(Screen):
    levelprogress = NumericProperty()
    reviewqueue = StringProperty()
    lessonqueue = StringProperty()
    levellength = NumericProperty()
    level = NumericProperty()
    windowsize = Window.size

    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        self.on_pre_enter()

    def on_pre_enter(self, *args):
        self.level = level
        self.levellength = fun.get_level_length(self.level)
        self.reviewqueue = str(len(reviewqueue))
        self.levelprogress = self.levellength - fun.get_remaining_in_level(self.level)

    def mycallback(self, *kwargs):
        widget = kwargs[1]
        widget.blink_size = 0
        widget.animationcolor = (1, 1, 1, 1)
        self.manager.transition = FallOutTransition()
        self.manager.current = self.next_screenname
        self.manager.transition = NoTransition()

    def animate_main_button(self, widget, name):
        # animates a button and calls the function of on_release afterwards
        animsize = self.ids.MainLabel.pos[0] + self.ids.MainLabel.size[0] - widget.pos[0]
        anim = Animation(animationcolor=science.levelcolor[level - 1], blink_size=animsize, duration=0.3)
        anim += Animation(duration=0.05)
        self.next_screenname = name
        anim.start(widget)
        anim.bind(on_complete=self.mycallback)

    def mainscreenspinner_click(self, name):
        if name == "About":
            self.manager.current = "About"
        if name == "Topics":
            self.manager.current = "TopicChoice"
        self.ids.levelspinner.text = ""
        # fixed bug: does not click if the same option was clicked right before
        # solution: reset levelspinner text to ""


class LessonQuizScreen(Screen):
    lessonanswer = ObjectProperty(None)
    lessoncorrectanswer = StringProperty()
    lessonemeaning = StringProperty()
    lessongmeaning = StringProperty()
    lessonqueuelabel = StringProperty()
    lessonquizqueue = ListProperty()
    lessonquizcolour = ListProperty()
    windowsize = Window.size
    submitting = StringProperty()

    def __init__(self, **kwargs):
        super(LessonQuizScreen, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.lessoncorrectanswer = ""
        self.lessongmeaning = " ? "
        self.lessonquizcolour = science.levelcolor[level-1]
        self.submitting = "Submit Answer"
        if len(lessonqueue) > 5:
            self.lessonquizqueue = lessonqueue[:5]
            self.lessonemeaning = self.lessonquizqueue[0][1]

        elif len(lessonqueue) == 0:
            self.lessonqueuelabel = "No"
            self.lessonquizqueue = []
            self.lessonemeaning = "No Lessons"

        else:
            self.lessonquizqueue = lessonqueue[:len(lessonqueue)]
            self.lessonemeaning = self.lessonquizqueue[0][1]
        self.lessonanswer.focus = True
        self.lessonqueuelabel = str(len(self.lessonquizqueue))
        Window.bind(on_key_down=self._on_keyboard_down)

    def do_one_lesson(self):
        if len(self.lessonquizqueue) != 0 and len(self.lessonanswer.text) > 0:
            correct = fun.do_a_lesson(self.lessonquizqueue[0], self.lessonanswer.text)
            self.lessoncorrectanswer = correct
            if correct == "Correct Answer":
                self.submitting = "Submit Answer"
                self.lessonquizcolour = science.levelcolor[level-1]
                self.lessonquizqueue.pop(0)
                lessonqueue.pop(0)
                self.lessongmeaning = ""
                self.sound = SoundLoader.load("Sound/correction/correct-answer.wav")
                self.sound.volume = volume
                self.sound.play()
                if len(self.lessonquizqueue) != 0:
                    self.lessonqueuelabel = str(len(self.lessonquizqueue))
                    self.lessonemeaning = self.lessonquizqueue[0][1]
                else:
                    self.lessonqueuelabel = "No"
                    self.lessonemeaning = ""
            else:
                self.sound = SoundLoader.load("Sound/correction/wrong-answer.wav")
                self.sound.volume = volume
                self.sound.play()
                Clock.schedule_once(self.settonext, 0.05)
                self.lessonquizcolour = (250/255, 90/255, 70/255, 1)
                self.lessongmeaning = self.lessonquizqueue[0][2]
        else:
            pass

    def update_text(self):
        self.lessonquizqueue.append(self.lessonquizqueue[0])
        self.lessonquizqueue.pop(0)
        self.lessonemeaning = self.lessonquizqueue[0][1]
        self.submitting = "Submit Answer"
        self.lessongmeaning = " ? "
        self.lessonanswer.text = ""
        self.lessonquizcolour = science.levelcolor[level-1]

    def settonext(self, *kwargs):
        self.submitting = "Next"

    def resettext(self, _):
        self.lessonanswer.text = ""

    def _on_keyboard_down(self, instance, keyboard, keycode, text, modifiers):
        if keycode == 40 and self.manager.current == "lessonquizscreen" and self.submitting == "Submit Answer":
            self.do_one_lesson()
            Clock.schedule_once(self.resettext)

        if keycode == 40 and self.manager.current == "lessonquizscreen" and self.submitting == "Next":
            self.update_text()
            Clock.schedule_once(self.resettext)


class StatisticsScreen(Screen):
    levelprogress = NumericProperty()
    reviewqueue = StringProperty()
    lessonqueue = StringProperty()
    levellength = NumericProperty()
    level = NumericProperty()
    windowsize = Window.size
    boxer = ObjectProperty(None)
    isplotthere = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.isplotthere = 0
        self.statisticsheight = 0.4 * self.windowsize[1]

    def on_pre_enter(self, *args):
        self.level = level
        self.levellength = fun.get_level_length(self.level)
        self.reviewqueue = str(len(reviewqueue))
        self.lessonqueue = str(len(lessonqueue))
        if self.isplotthere == 0:
            self.add_plot_review24()
            self.add_plot_levelprogression()

    def add_plot_levelprogression(self):
        self.ids.statistics1.clear_widgets()
        self.points = fun.progression2()
        if max(self.points)[0] == 0:
            self.maxpoints = 4
        else:
            self.maxpoints = max(self.points)[0]
        self.progressgraph = Graph(xlabel='SRS Stage', ylabel='Items',
                      x_ticks_major=1, y_ticks_major=25,
                      x_grid_label=True, y_grid_label=True,
                      x_grid=True, y_grid=True, padding=5,
                      xmin=0, xmax=self.maxpoints+1, ymin=0, ymax=max(self.points, key=lambda tup: tup[1])[1]+5, label_options={'color': [0, 0, 0, 1]})
        self.ids.statistics1.add_widget(self.progressgraph)
        self.progressplot = BarPlot(color=science.levelcolor[level - 1], bar_width=20, bar_spacing=0.100)
        self.progressplot.points = (self.points)
        self.progressgraph.add_plot(self.progressplot)
        pass

    def add_plot_review24(self):
        self.ids.statistics2.clear_widgets()
        self.datepoints = fun.upcoming_reviews()
        # if self.datepoints == [(0, 0)]:
        #     self.statisticsheight = science.menubarheight
        #     self.emptylabel = Label(text="No new Reviews in the next 24 houers.", color=(0, 0, 0, 1), width=science.menubarheight,
        #                             height=science.menubarheight, text_size=self.size, halign='left', valign='top')
        #     self.ids.statistics2.add_widget(self.emptylabel)
        # else:
        #ymin=0,xmin=0,x_ticks_minor=1,y_ticks_minor=1,
        self.statisticsheight = 0.4*self.windowsize[1]
        self.dategraph = Graph(xlabel='Hours', ylabel='Items',
                      x_ticks_major=3,  y_ticks_major=5,
                      x_grid_label=True, y_grid_label=True,
                      x_grid=True, y_grid=True, padding=5,
                      xmax=24,  ymax=max(self.datepoints, key=lambda tup: tup[1])[1]+5, label_options={'color': [0,0,0,1]})
        self.ids.statistics2.add_widget(self.dategraph)
        self.dateplot = BarPlot(color=science.levelcolor[level - 1], bar_width=20, bar_spacing=0.100)
        self.dateplot.points = (self.datepoints)
        self.dategraph.add_plot(self.dateplot)
        pass


class ExtrasScreen(Screen):
    windowsize = Window.size
    gamemode = StringProperty("MemoryScreen")
    useallvocab = BooleanProperty()
    useallcolor = (0.5, 0.5, 0.5, 1)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def useallvocabulary(self):
        self.useallvocab = not self.useallvocab


class MemoryScreen(Screen):
    windowsize = Window.size
    memoryitems = ListProperty()
    englishmemory = StringProperty()
    germanmemory = StringProperty()
    randomeng = ListProperty()
    randomde = ListProperty()
    all_subjects = BooleanProperty(False)
    countercorrect = NumericProperty()
    counterwrong = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.memoryitems = fun.fiverandomitems()
        self.englishbuttonid = None
        self.germanbuttonid = None
        self.englishmemory = ""
        self.germanmemory = ""
        self.buttoncolor = science.levelcolor[level-1]

    def on_pre_enter(self, *args):
        self.all_subjects = self.manager.get_screen("ExtrasScreen").useallvocab

    def on_enter(self, *args):
        self.countercorrect = 0
        self.counterwrong = 0
        self.buttoncolor = science.levelcolor[level - 1]
        self.add_item_buttons()
        Clock.schedule_once(self.addcanvas, 0.1)

    def on_leave(self, *args):
        self.ids.memorygrid1.clear_widgets()
        self.ids.memorygrid2.clear_widgets()

    def addrectangle(self, englishbutton, color):
        englishbutton.canvas.before.add(Color(rgba=color))
        englishbutton.canvas.before.add(RoundedRectangle(size=englishbutton.size, pos=englishbutton.pos,
                                                         radius=[(englishbutton.size[1] + 100) * 0.1]))

    def addrectanglewithborder(self, englishbutton, color):
        englishbutton.canvas.before.add(Color(rgba=(1, 0, 0, 1)))
        englishbutton.canvas.before.add(Line(rounded_rectangle=(englishbutton.pos[0], englishbutton.pos[1], englishbutton.size[0], englishbutton.size[1], (englishbutton.size[1] + 100) * 0.1), width=2))
        englishbutton.canvas.before.add(Color(rgba=color))
        englishbutton.canvas.before.add(RoundedRectangle(size=englishbutton.size, pos=englishbutton.pos,
                                                         radius=[(englishbutton.size[1] + 100) * 0.1]))

    def addcanvas(self, *kwargs):
        for englishbutton in self.ids.memorygrid1.children:
            self.addrectangle(englishbutton, self.buttoncolor)
        for englishbutton in self.ids.memorygrid2.children:
            self.addrectangle(englishbutton, self.buttoncolor)

    def use_all_subjects(self):
        self.all_subjects = not self.all_subjects

    def myenglishmemoryisgreat(self, text):
        # resets last pressed button color
        if self.englishbuttonid is not None:
            self.englishbuttonid.canvas.before.clear()
            self.addrectangle(self.englishbuttonid, self.buttoncolor)

        # sets pressed button color
        text.canvas.before.clear()
        self.addrectanglewithborder(text, self.buttoncolor)
        # gets text of button
        self.englishmemory = str(text.text)[1:len(text.text)]

        # correct if a corresponding german item is given
        if self.germanmemory != "":
            for i in self.memoryitems:
                if fun.unsplitmyword(self.englishmemory) == i[1]:
                    if fun.unsplitmyword(self.germanmemory) == i[2]:
                        # item correctly answered, disable the eng and the ger button
                        text.disabled = True
                        self.germanbuttonid.disabled = True
                        self.germanbuttonid.canvas.before.clear()
                        text.canvas.before.clear()
                        self.addrectangle(self.germanbuttonid, (0, 0, 0, 0.5))
                        self.addrectangle(text, (0, 0, 0, 0.5))
                        self.countercorrect += 1
                        if self.countercorrect == 5:
                            self.on_leave()
                            self.on_enter()
                    else:
                        # item wrongly answered, set color to red
                        self.germanbuttonid.canvas.before.clear()
                        text.canvas.before.clear()
                        self.addrectangle(self.germanbuttonid, (1, 0, 0, 0.5))
                        self.addrectangle(text, (1, 0, 0, 0.5))
                        self.counterwrong += 1
                    self.englishmemory = ""
                    self.germanmemory = ""
                    self.germanbuttonid = None
                    self.englishbuttonid = None

        else:
            self.englishbuttonid = text

    def mygermanmemoryisgreat(self, text):
        # gets text of the german button and checks if last pressed eng button is the right one
        if self.germanbuttonid is not None:
            self.germanbuttonid.canvas.before.clear()
            self.addrectangle(self.germanbuttonid, self.buttoncolor)
        text.canvas.before.clear()
        self.addrectanglewithborder(text, self.buttoncolor)
        self.germanmemory = str(text.text)[1:len(text.text)]
        self.germanbuttonid = text

        if self.englishmemory != "":
            for i in self.memoryitems:
                if fun.unsplitmyword(self.germanmemory) == i[2]:
                    if fun.unsplitmyword(self.englishmemory) == i[1]:
                        # item right disable the eng and the ger button
                        text.disabled = True
                        self.englishbuttonid.disabled = True
                        text.canvas.before.clear()
                        self.addrectangle(text, (0, 0, 0, 0.5))
                        self.englishbuttonid.canvas.before.clear()
                        self.addrectangle(self.englishbuttonid, (0, 0, 0, 0.5))
                        self.countercorrect += 1
                        if self.countercorrect == 5:
                            self.on_leave()
                            self.on_enter()
                    else:
                        # item wrong set color to red
                        text.canvas.before.clear()
                        self.addrectangle(text, (1, 0, 0, 0.5))
                        self.englishbuttonid.canvas.before.clear()
                        self.addrectangle(self.englishbuttonid, (1, 0, 0, 0.5))
                        self.counterwrong += 1

                    self.englishmemory = ""
                    self.germanmemory = ""
                    self.germanbuttonid = None
                    self.englishbuttonid = None
        else:
            self.germanbuttonid = text

    def add_item_buttons(self):
        self.englishmemory = ""
        self.germanmemory = ""
        # getting some random subjects of all subjects or just the srs > 1 available
        if self.all_subjects is False:
            self.memoryitems = fun.fiverandomitems()
        else:
            self.memoryitems = fun.fiverandomsubjects()

        # shuffle them in two lists
        self.randomeng = []
        self.randomde = []
        for x in self.memoryitems:
            self.randomeng.append(x[1])
            self.randomde.append(x[2])
        shuffle(self.randomeng)
        shuffle(self.randomde)

        # add buttons to the predefined gridlayouts for all the subjects
        for eng in self.randomeng:
            englishbutton = (Button(text=" {}".format(str(fun.splitmyword(eng))), on_press=self.myenglishmemoryisgreat,
                                         height="72dp",
                                         color=(0, 0, 0, 1), background_normal='', background_color=(1, 1, 1, 0),
                                         halign='center', valign='center'))
            self.ids.memorygrid1.add_widget(englishbutton)
        for de in self.randomde:
            germanbutton = (Button(text=" {}".format(str(fun.splitmyword(de))),
                                        height="72dp",
                                        color=(0, 0, 0, 1), background_normal='', background_color=(1, 1, 1, 0),
                                        halign='center', valign='center', on_press=self.mygermanmemoryisgreat))
            self.ids.memorygrid2.add_widget(germanbutton)


class QuizStatAdvancedScreen(Screen):
    percentage = NumericProperty()
    stats = ListProperty()
    extrabuttoncolor = ListProperty()
    all_subjects = BooleanProperty()

    def __init__(self, **kwargs):
        super(QuizStatAdvancedScreen, self).__init__(**kwargs)
        self.stats = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.percentage = 100
        self.extrabuttoncolor = (0, 0, 0, 0.5)
        self.all_subjects = False
        pass

    def on_pre_enter(self, *args):
        self.statmaths()
        pass

    def statmaths(self):
        number = self.stats.count(1)
        self.percentage = (number/10)*100

    def use_all_subjects(self):
        SoundcheckScreen.all_subjects2 = not self.all_subjects


class SoundcheckScreen(Screen):
    soundlink = StringProperty()
    sound = ObjectProperty()
    all_subjects2 = BooleanProperty(False)
    buttoncolor = ListProperty()

    def __init__(self, **kwargs):
        super(SoundcheckScreen, self).__init__(**kwargs)
        self.memoryitems = fun.fiverandomsubjects()
        self.soundlink = ""
        self.counterwrong = 0
        self.overallcounter = 0
        self.rightorwrong = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def on_pre_enter(self, *args):
        self.all_subjects2 = self.manager.get_screen("ExtrasScreen").useallvocab
        self.ids.soundgrid.clear_widgets()
        self.add_sound_buttons()
        self.ids.soundgrid.add_widget(self.englayout)
        self.counterwrong = 0
        self.drawbottomcanvas()
        self.buttoncolor = science.levelcolor[level-1][0:3] + (0.5,)
        Clock.schedule_once(self.addbuttoncanvas, 0.1)

    def addrectangle(self, englishbutton, color):
        englishbutton.canvas.before.add(Color(rgba=color))
        englishbutton.canvas.before.add(RoundedRectangle(size=englishbutton.size, pos=englishbutton.pos,
                                                         radius=[(englishbutton.size[1] + 100) * 0.1]))

    def addbuttoncanvas(self, *kwargs):
        for englishbutton in self.englayout.children:
            self.addrectangle(englishbutton, self.buttoncolor)

    def drawbottomcanvas(self):
        self.ids.canvasgrid.canvas.clear()
        for count, i in enumerate(self.rightorwrong):
            if i == 0:
                self.ids.canvasgrid.canvas.add(Color(rgba=(0, 0, 0, 0.5)))
            elif i == 1:
                # correct answer colored green
                self.ids.canvasgrid.canvas.add(Color(rgba=(0, 1, 0, 0.5)))
            elif i == 2:
                # wrong answer colored red
                self.ids.canvasgrid.canvas.add(Color(rgba=(1, 0, 0, 0.5)))
            self.ids.canvasgrid.canvas.add(Rectangle(pos=[science.windowsize[0]/2-science.windowsize[0]/20*5+count*science.windowsize[0]/20, science.windowsize[1]/10],
                                                     width=1.,
                                                     size=[science.windowsize[0]/25, science.windowsize[0]/25]))

    def resetwindow(self):
        if self.overallcounter == 10:
            #SoundcheckIntroScreen.stats = self.rightorwrong
            self.manager.current = "ExtrasScreen"
            self.overallcounter = 0
            self.rightorwrong = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def memory(self, buttonname):
        # checks if answer correct or not
        if buttonname.text[1:len(buttonname.text)] == self.memoryitems[0][2]:
            self.overallcounter += 1
            self.rightorwrong[self.overallcounter-1] = 1
            self.on_pre_enter()
            self.resetwindow()
        else:
            buttonname.disabled = True
            buttonname.canvas.before.clear()
            self.addrectangle(buttonname, (1, 0, 0, 0.5))
            self.counterwrong += 1
            if self.counterwrong > 0:
                self.overallcounter += 1
                self.rightorwrong[self.overallcounter-1] = 2
                self.on_pre_enter()
                self.resetwindow()

    def reset_items(self):
        # gets new items from the database
        if self.all_subjects2 is False:
            self.memoryitems = fun.fiverandomitems()
        else:
            self.memoryitems = fun.fiverandomsubjects()

    def add_sound_buttons(self):
        self.reset_items()

        # new list in which items get shuffled and then displayed
        self.randomeng = []
        for x in self.memoryitems:
            self.randomeng.append(x[2])
        shuffle(self.randomeng)

        # create layout with buttons for all the subjects
        self.englayout = GridLayout(cols=1, padding="8dp", spacing="8dp")
        for eng in self.randomeng:
            self.englishbutton = (Button(text=" {}".format(str(eng)), on_press=self.memory,
                                         color=(0, 0, 0, 1),
                                         background_normal='', background_color=(1, 1, 1, 0),
                                         halign='center', valign='center'))
            self.englishbutton.bind(size=self.englishbutton.setter('text_size'))
            self.englayout.add_widget(self.englishbutton)
        self.play_sound()

    def play_sound(self):
        if self.sound is not None:
            self.sound.stop()
        self.soundlink = self.memoryitems[0][3]
        self.sound = SoundLoader.load(self.soundlink)
        self.sound.volume = volume
        self.sound.play()


class SaveScreen(Screen):
    updating = ObjectProperty(None)
    updateanswer = StringProperty()
    selection = StringProperty("...")
    path = ObjectProperty(None)
    androidpath = primary_ext_storage

    def __init__(self, **kwargs):
        super(SaveScreen, self).__init__(**kwargs)

    def on_pre_enter(self, *args):
        self.updateanswer = ""

    def on_pre_leave(self, *args):
        updatequeues()

    def updatequeues(self):
        updatequeues()


class TopicChoice(Screen):

    def __init__(self, **kwargs):
        super(TopicChoice, self).__init__(**kwargs)

    def mycallback(self, *kwargs):
        # called when anim of button finished
        widget = kwargs[1]
        widget.blink_size = 0
        widget.animationcolor = (1, 1, 1, 1)
        self.manager.transition = FallOutTransition()
        # add functionalities for when anim finished here
        self.manager.current = "mainscreen"
        self.manager.transition = NoTransition()

    def animate_level_button(self, widget, name):
        # animates a button and calls the function of on_release afterwards
        animsize = self.ids.MainLabel.pos[0] + self.ids.MainLabel.size[0] - widget.pos[0]
        anim = Animation(animationcolor=science.levelcolor[level - 1], blink_size=animsize, duration=0.3)
        anim += Animation(duration=0.05)
        anim.start(widget)
        anim.bind(on_complete=self.mycallback)


class Tutorial(Screen):
    def __init__(self, **kwargs):
        super(Tutorial, self).__init__(**kwargs)


class DevMode(Screen):
    # screen for manipulating the database as a developer
    updating = ObjectProperty(None)
    updateanswer = StringProperty()
    buttonpressed = StringProperty("")

    def __init__(self, **kwargs):
        super(DevMode, self).__init__(**kwargs)
        Window.bind(on_key_down=self._on_key_down)

    def updatequeue(self, *args):
        updatequeues()

    def on_enter(self, *args):
        self.updating.keyboard_mode = "managed"
        self.updating.show_keyboard()

    def on_leave(self, *args):
        self.updating.hide_keyboard()

    def _on_key_down(self, instance, keyboard, keycode, text, modifiers):
        if self.manager.current == "DevMode":
            self.buttonpressed = str(keycode)


class About(Screen):
    # about the app and acknoledgements
    abouttext = StringProperty("")

    def __init__(self, **kwargs):
        super(About, self).__init__(**kwargs)
        #Window.bind(on_key_down=self._on_key_down)

    def on_enter(self, *args):
        self.abouttext = fun.about()


class SpinnerOptions(SpinnerOption):
    def __init__(self, **kwargs):
        super(SpinnerOptions, self).__init__(**kwargs)
        self.background_normal = ''
        self.background_color = [1, 1, 1, 0.9]
        self.color = [0, 0, 0, 1]
        self.height = 0.1*Window.size[1]
        # Set designoptions for spinnerwidget


class SpinnerDropdown(DropDown):
    def __init__(self, **kwargs):
        super(SpinnerDropdown, self).__init__(**kwargs)
        self.auto_width = False
        self.width = 0.4*Window.size[0]
        # Set the measurements of spinnerwidget


class SpinnerWidget(Spinner):
    def __init__(self, **kwargs):
        super(SpinnerWidget, self).__init__(**kwargs)
        self.dropdown_cls = SpinnerDropdown
        self.option_cls = SpinnerOptions
        # im spinnerwidget


class WindowManager(ScreenManager):
    def on_motion(self, etype, me):
        science.topboxlabelname = fun.topboxproperties(self.root.current)[0]
        print(science.topboxlabelname)
        pass


Config.set('kivy', 'exit_on_escape', '0')
Config.set('kivy', 'keyboard_mode', '')
Config.write()


class science(App):
    answer = ListProperty()
    guidetext = StringProperty()
    levelnames = ["General Science", "Job Interview", "Medicine", "Electronics", "Chemistry"]
    lessonqueue = StringProperty()
    mainscreen_levelname = StringProperty(str(levelname[0][0]))
    windowsize = Window.size
    opsystemname = os.name
    platformname = platform.system()
    soundicon = StringProperty('Images/volume-high.png')
    iconsize = ("24dp", "24dp")
    levelcolor = [(0, 170/255, 160/255, 1), (10/255, 168/255, 0/255, 0.75), (36/255, 168/255, 0/255, 0.66), (173/255, 191/255, 10/255, 0.75), (189/255, 157/255, 0/255, 0.74)]
    menubarheight = "56dp"
    roundedbuttoncolor = ListProperty()
    topboxlabelname = StringProperty("Home")

    def __init__(self, **kwargs):
        super(science, self).__init__(**kwargs)
        self.lessonqueue = str(len(lessonqueue))
        self.roundedbuttoncolor = self.levelcolor[level-1]
        updatequeues()

    def topboxer(self, name):
        # gets called when leaving a screen to change name in the topbox
        self.topboxlabelname = fun.topboxproperties(name)[0]

    def levelclicked(self, name):
        global lessonqueue
        global level
        global levelname
        lessonqueue = fun.getlessonqueue(self.levelnames.index(name)+1)
        level = self.levelnames.index(name)+1
        self.roundedbuttoncolor = self.levelcolor[level-1]
        self.mainscreen_levelname = name
        self.lessonqueue = str(len(lessonqueue))
        MainScreen.on_pre_enter(self)

    def soundmuter(self):
        global volume
        if volume == 1:
            volume = 0
            self.soundicon = 'Images/volume-off.png'
        elif volume == 0:
            volume = 1
            self.soundicon = 'Images/volume-high.png'

    def searcher(self):
        # search function for search popup
        self.searchlayout = GridLayout(cols=1, size_hint_y=None)
        self.searchlayout.bind(minimum_height=self.searchlayout.setter('height'))
        for i in self.answer[0]:
            self.label = (Button(text="{}\n{}".format(str(i[1]), str(i[2])), on_press=self.open_search_button,
                                 size_hint_y=None, height="56dp", color=(0, 0, 0, 1),
                                 background_normal='', background_color=(1, 1, 1, 1),
                                 halign='left', valign='center'))
            self.label.bind(size=self.label.setter('text_size'))
            self.searchlayout.add_widget(self.label)

    def open_search_button(self, text):
        # activated when a searchresult in the searchpopup gets clicked
        searchresult = fun.get_item_with_emeaning(text.text.splitlines()[0].strip())
        if text.height == 120.0:
            text.height = "56dp"
            text.text = "{}\n{}".format(str(searchresult[0][0]), str(searchresult[0][1]))
            text.background_color = (1, 1, 1, 1)
        else:
            text.background_color = (0, 0, 0, 0.1)
            text.height = "120dp"
            if searchresult[0][2] == " ":
                searchresult = [(searchresult[0][0], searchresult[0][1], "No Synonym", searchresult[0][3], searchresult[0][4], searchresult[0][5])]
            if searchresult[0][3] == " ":
                searchresult = [(searchresult[0][0], searchresult[0][1], searchresult[0][2], "No Synonym",  searchresult[0][4], searchresult[0][5])]
            text.text = "{}\n{}\n{}\n{}\nSRS stage: {}\nTotal times wrong: {}".format(
                                                                                 str(searchresult[0][0]),
                                                                                 str(searchresult[0][1]),
                                                                                 str(searchresult[0][2]),
                                                                                 str(searchresult[0][3]),
                                                                                 str(searchresult[0][4]),
                                                                                 str(searchresult[0][5]))

    def build(self):
        #self.icon = r'Images\icon0406nummer2.ico'
        return Builder.load_file("scienceenglish.kv")


if __name__ == "__main__":
    if hasattr(sys, '_MEIPASS'):
        resource_add_path(os.path.join(sys._MEIPASS))
    science().run()
