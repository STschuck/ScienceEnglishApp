# -*- coding: utf-8 -*-
"""
Created on Sun Jan 30 16:39:01 2022

@author: Simon
"""

import datetime as d
import numpy as np
import sqlite3
from difflib import SequenceMatcher
from random import sample, shuffle
import json
import os
import platform

app_path = os.path.dirname(os.path.abspath(__file__))
# possible solution for --onefile pyinstaller bug not updating database
# if platform.system() == "Windows":
#     app_path = os.path.join(os.environ['APPDATA'], 'scienceenglish')
#     if not os.path.exists(app_path):
#          os.makedirs(app_path)
connection = sqlite3.connect(os.path.join(app_path, 'All.db'))
cursor = connection.cursor()
time = d.datetime.now().strftime("%Y-%m-%d %H:00:00")


def tutorialintroduction():
    tutorialtext = """Welcome to the Science English App!
In this tutorial, the features of this app will be explained.
Make sure to test them all out and have fun learning new vocabulary!"""

    return tutorialtext


def tutoriallesson():
    tutorialtext = """This is the Lesson Section.
Go here to learn new vocabulary and queue them up in our Spaced Repetition System.
After 4 hours, the lesson will be available in the Review Section.
It works like a box with index cards. For every right answer, the time until the next review will increase.
The goal is to reach Stage 8 of the SRS System!"""

    return tutorialtext


def tutorialreview():
    tutorialtext = """In the Review Section, previously learned and reviewed vocabulary will appear again.
Try to do your reviews as often as you can. 
With constant review, the words will be cemented in your brain and you will not forget them anymore."""

    return tutorialtext


def tutorialstatistics():
    tutorialtext = """The statistics will show an overview of your progression and your upcoming reviews in the next 24 hours.
Here you want to go to plan when you will do your next learning session or just to be happy about how far you have come already.  
"""

    return tutorialtext


def tutorialextra():
    tutorialtext = """We developed some fun little extra tasks you can do when you are bored or want to invest some more time.
In here is a quiz in which you have to assign English words to their matching german counterpart.
The second quit will test your listening ability. You will hear a word and need to match it with the right reading.
"""

    return tutorialtext


def tutoriallevel():
    tutorialtext = """Click on this button to change the subject.
All vocabulary is organized in certain themes, so you only have to learn what you really care about.
This will only affect the lessons that you learn next. The reviews will come up no matter which subject you are in.
"""

    return tutorialtext


def tutorialsearch():
    tutorialtext = """This is the search function. Type in a word and you will get a result if the word is in the database.
"""

    return tutorialtext


def tutorialsave():
    tutorialtext = """To save your progress or transit it to an other device click on this button. 
The export fuction will create a file that you can save anywhere you want.
With the import function you can import those files again to update your progress.
"""

    return tutorialtext


def levelfinishedtext():
    return """No Vocabulary left to learn in this level.
    
Please choose another one.
To do that, you have to go 
back to the Homescreen and click the
Burger Menu in the top left corner.
We hope you had fun in this level!
"""


def about():
    return "Welcome to ScienceEnglish 1.0.0.\n\n" \
           "ScienceEnglish is an App to help you learn english vocabulary that are important to your field of study.\n"\
            "Scienceeglish was written by Simon Tschuck.\n"\
            "Mail: simon.tschuck@gmail.com\n"\
            "This App is completly free to use. "\
            "For more details check the imprint and acknowledgements."



def imprint():
    return """Welcome to ScienceEnglish 1.0.0.

Imprint following soon!
"""

def acknowledgements():
    return """Welcome to ScienceEnglish 1.0.0.

This app uses following Open source 
third party components and sources:

- Kivy 
- Kivy Garden Graph
- Google Text to Speech
- Google Translator
- NLTK WordNet
- Numpy
- https://opentextbc.ca/
- wikipedia
"""

def get_time():
    print("Time right now: " + str(d.datetime.now()))
    print("Used Time: " + str(time))
    return d.datetime.now(), time 


def getreviewqueue():
    c = """SELECT SID FROM Review WHERE Date<?"""
    cursor.execute(c, (d.datetime.now(),))
    reviews = cursor.fetchall()
    return reviews


def get_all_reviews():
    c = """SELECT Subject.SID, Subject.EMeaning, Subject.GMEaning, Subject.srsstage, Subject.GSynonym, Review.Timeswrong, Review.Timeswronginsession FROM Subject, Review  WHERE Review.SID=Subject.SID and Review.Date<?"""
    cursor.execute(c, (d.datetime.now(),))
    allcontents = cursor.fetchall()
    shuffle(allcontents)
    return allcontents


def get_item_with_emeaning(emeaning):
    c = """SELECT Subject.EMeaning, Subject.GMEaning, Subject.ESynonym, Subject.GSynonym, Subject.srsstage, Review.Timeswrong FROM Subject, Review  WHERE Review.SID=Subject.SID and Subject.EMeaning=?"""
    cursor.execute(c, (emeaning,))
    result = cursor.fetchall()
    if not result:
        c = """SELECT EMeaning, GMEaning, ESynonym, GSynonym, srsstage FROM Subject WHERE EMeaning=?"""
        cursor.execute(c, (emeaning,))
        result = cursor.fetchall()
        result = [result[0] + (0,)]
    return result


def get_first_review():
    try: 
        content = get_all_reviews()
        content = content[0]
        return content 
    except:         
        #print("No Reviews left")
        return None


def show_review_length():
    content = get_all_reviews()
    return len(content)


def set_review_date(sid, date):
    date = date.strftime("%Y-%m-%d %H:00:00")
    c = """UPDATE Review SET Date=? WHERE SID=?"""
    cursor.execute(c, (date, sid))
    connection.commit()


def set_srs_stage(sid, srsstage):
    c = """UPDATE Subject SET srsstage=? WHERE SID=?"""
    cursor.execute(c, (srsstage, sid))
    connection.commit()   


def new_date(srsstage):
    if srsstage == 1:
        new_time = d.datetime.now()+d.timedelta(hours=4)
        
    elif srsstage == 2:
        new_time = d.datetime.now()+d.timedelta(hours=8)
        
    elif srsstage == 3:
        new_time = d.datetime.now()+d.timedelta(hours=12)
        
    elif srsstage == 4:
        new_time = d.datetime.now()+d.timedelta(days=1)
        
    elif srsstage == 5:
        new_time = d.datetime.now()+d.timedelta(days=7)
        
    elif srsstage == 6:
        new_time = d.datetime.now()+d.timedelta(days=14)

    elif srsstage == 7:
        new_time = d.datetime.now() + d.timedelta(days=28)

    elif srsstage == 8:
        new_time = "burned"
        #burning items

    new_time = new_time.strftime("%Y-%m-%d %H:00:00")
    
    return new_time


def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def do_a_review(review, answer):
    # review[sid, english meaning, german meaning, srsstage, gsynonym, Timeswrong, Timeswronginssession]
    # should get an answer, correct, and update list
    srsstage = review[3]
    if similar(answer, review[2]) > 0.7 or similar(answer, review[4]) > 0.7:
        if review[6] == 0:
            srsstage += 1
            c = """UPDATE Subject SET srsstage=? WHERE SID=?"""
            cursor.execute(c, (srsstage, review[0]))
            connection.commit()
            c = """UPDATE Review SET Date=? WHERE SID=?"""
            cursor.execute(c, (new_date(srsstage), review[0]))
            connection.commit()

        elif 1 <= review[6] <= 3:
            if srsstage > 1:
                srsstage -= 1
            c = """UPDATE Subject SET srsstage=? WHERE SID=?"""
            cursor.execute(c, (srsstage, review[0]))
            connection.commit()
            c = """UPDATE Review SET Date=?, Timeswronginsession=? WHERE SID=?"""
            cursor.execute(c, (new_date(srsstage), 0, review[0]))
            connection.commit()  
            
        elif review[6] > 3:
            if srsstage > 2:
                srsstage -= 2
            c = """UPDATE Subject SET srsstage=? WHERE SID=?"""
            cursor.execute(c, (srsstage, review[0]))
            connection.commit()
            c="""UPDATE Review SET Date=?, Timeswronginsession=? WHERE SID=?"""
            cursor.execute(c, (new_date(srsstage), 0, review[0] ))
            connection.commit()  
        a = "Correct answer"
        return a
    else:
        c = """UPDATE Review SET Timeswrong=?, Timeswronginsession=? WHERE SID=?"""
        cursor.execute(c, (review[5]+1, review[6]+1, review[0]))
        connection.commit() 
        return "Wrong answer"


def getlessonqueue(level):
    c = """SELECT SID, EMeaning, GMeaning, ESynonym, GSynonym, Level, Definition, SoundLink FROM Subject WHERE srsstage=0 AND Level=?"""
    cursor.execute(c, (level, ))
    lesson = cursor.fetchall() 
    return lesson

#updates srssrtage to 1 and moves item into reviewqueue
def do_a_lesson(lesson, answer):
    answer = answer.lower()
    if similar(lesson[2],answer) > 0.7 or similar(lesson[4],answer) > 0.8 :
        #move to review q
        cursor.execute('SELECT max(RID) FROM Review')
        RID = cursor.fetchone()[0]
        if RID == None:
            RID = 1
        else:
            RID += 1
        newreview = (RID, lesson[0], new_date(1), 0, 0)
        c = "INSERT INTO Review (rid, sid, date,timeswrong ,Timeswronginsession ) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(c, newreview)
        connection.commit()
        
        c = """UPDATE Subject SET srsstage=? WHERE SID=?"""
        cursor.execute(c, (1, lesson[0]))
        connection.commit()
        return "Correct Answer"
    else: 
        return "Wrong Answer"
#cursor.executemany(c,newreview )   
    
def search_for(searchterm):
    c="""SELECT SID, EMeaning, GMeaning, ESynonym, GSynonym FROM Subject WHERE EMeaning LIKE ? """
    cursor.execute(c, ("%"+searchterm+"%", ))
    result = cursor.fetchall()
    if len(result) == 0:         
        c = """SELECT SID, EMeaning, GMeaning, ESynonym, GSynonym FROM Subject WHERE GMeaning LIKE ?"""
        cursor.execute(c, ("%"+searchterm+"%", ))
        result = cursor.fetchall()
    if len(result) == 0:
        c = """SELECT SID, EMeaning, GMeaning, ESynonym, GSynonym FROM Subject WHERE ESynonym LIKE ? """
        cursor.execute(c, ("%"+searchterm+"%", ))
        result = cursor.fetchall()
    if len(result) == 0:
        c = """SELECT SID, EMeaning, GMeaning, ESynonym, GSynonym FROM Subject WHERE GSynonym LIKE ? """
        cursor.execute(c, ("%"+searchterm+"%", ))
        result = cursor.fetchall()       
    
    if len(result) > 0:
        result = result #string
    else:
        result = [(0, "No Result", "", "", "")]
    
    return result


def get_level_length(level):
    c = """SELECT SID FROM Subject WHERE Level=?"""
    cursor.execute(c, (level, ))
    result = cursor.fetchall()       
    levellength = len(result)
    return levellength


def get_remaining_in_level(level):
    c = """SELECT SID FROM Subject WHERE Level=? and srsstage=0"""
    cursor.execute(c, (level, ))
    result = cursor.fetchall()       
    levellength = len(result)
    return levellength


def get_current_level():
    cursor.execute('SELECT min(Level) FROM Subject WHERE srsstage=0')
    level = cursor.fetchone()[0]
    cursor.execute('SELECT Name FROM Level WHERE Level=?', (level,))
    levelname = cursor.fetchall()
    if level is None:
        level = 1
    return level, levelname


def reset_all_to_lessons():
    # clear all reviews
    cursor.execute("""SELECT RID FROM Review """)
    connection.commit()
    allrid = cursor.fetchall()
    cursor.executemany("""DELETE FROM Review WHERE (?)""", (allrid))

    # set all srsstages to 0
    cursor.execute("""SELECT SID FROM Subject""")
    connection.commit()
    allsid = cursor.fetchall()
    cursor.executemany("""UPDATE Subject SET srsstage=0 WHERE SID=?""", (allsid))


def reset_all_reviews():
    # reset date of all reviews
    cursor.execute("""SELECT RID FROM Review """)
    connection.commit()
    allrid = cursor.fetchall()
    cursor.executemany("""UPDATE Review SET Date=? WHERE RID=?""", (time, allrid))

    # set all srsstages to 1
    cursor.execute("""SELECT SID FROM Subject""")
    connection.commit()
    allsid = cursor.fetchall()
    cursor.executemany("""UPDATE Subject SET srsstage=1 WHERE SID=?""", (allsid))


def set_items_to_reviews():
    c = """SELECT SID FROM Subject WHERE srsstage=0 """
    cursor.execute(c)
    result = cursor.fetchall()
    for i in range(10):
        cursor.execute('SELECT max(RID) FROM Review')
        rid = cursor.fetchone()[0]
        if rid is None:
            rid = 1
        else:
            rid += 1
        newreview = (rid, result[i][0], d.datetime.now().strftime("%Y-%m-%d %H:00:00"), 0, 0)
        c = "INSERT INTO Review (rid, sid, date,timeswrong ,Timeswronginsession ) VALUES (?, ?, ?, ?, ?)"
        cursor.execute(c, newreview)
        connection.commit()

        c = """UPDATE Subject SET srsstage=? WHERE SID=?"""
        cursor.execute(c, (1, result[i][0]))
        connection.commit()


def upcoming_reviews():
    c = """SELECT Date, COUNT(Date) FROM Review WHERE ? < Date AND Date < ? GROUP BY Date"""#,COUNT(SID)
    cursor.execute(c, (d.datetime.now()+d.timedelta(hours=1), d.datetime.now()+d.timedelta(hours=24)))
    reviews_24 = cursor.fetchall()
    reviews_24.insert(0, (d.datetime.now().strftime("%Y-%m-%d %H:00:00"), len(get_all_reviews())))
    reviews = []
    now = int(d.datetime.now().strftime("%H"))
    day = int(d.datetime.now().strftime("%d"))
    for i in range(len(reviews_24)):
        j = reviews_24[i][0]
        if day == int(j[8:10]):
            reviews.append((int(j[11:13]) - now, reviews_24[i][1]))
        else:
            reviews.append((24 - now + int(j[11:13]), reviews_24[i][1]))
    return reviews
    pass


# def plot_24():
#     z = upcoming_reviews()
#     fig, ax = plt.subplots()
#     ax.bar(datestr2num(z[1]), z[0], width=0.025, color=(0, 170/255,160/255))
#     ax.xaxis_date()
#     ax.yaxis.set_major_locator(MaxNLocator(integer=True))
#     ax.xaxis.set_major_locator(HourLocator(interval=4))
#     ax.xaxis.set_minor_locator(HourLocator(interval=1))
#     ax.xaxis.set_major_formatter(DateFormatter('%H:%M'))
#     ax.set_xlabel("")
#     ax.set_title("Upcoming Reviews")
#     pass


# def progression():
#     progress = []
#     barheight = [0, 0, 0, 0, 0]
#     r = [1, 2, 3, 4, 5]
#     # get list with lists per first 7 srstage with amount in level
#     fig, ax = plt.subplots()
#     for i in range(0, 7):
#         i = 7-i
#         c = """SELECT level FROM Subject WHERE srsstage=? """
#         cursor.execute(c, (i,))
#         srslevel = cursor.fetchall()
#         progressperlevel = []
#         # counting items of certain srsstage of level 1 to 6 and sets into relation of complete levellength
#         for j in range(1, 6):
#             progressperlevel.append(srslevel.count((j,))/int(get_level_length(j)))
#         #progress.append(progressperlevel)
#         ax.bar(r, progressperlevel, bottom=barheight, width=0.9, color=(0, 1-i*0.1, 0, 1))
#         # sets up the height for the next barplot
#         barheight = np.add(barheight, progressperlevel).tolist()
#     names = ["General", "Job Interview", "Medicine", "Electronics", "Chemistry"]
#     ax.set_xticks(r, names)
#     ax.set_ylim(0, 1)
#     ax.set_title("Progress")
#     pass


def progression2():
    c = """SELECT srsstage,COUNT(SID) FROM Subject GROUP BY srsstage  """ #, srsstage
    cursor.execute(c)
    result = cursor.fetchall()
    return result


def fiverandomitems():
    c = """SELECT SID, EMeaning, GMeaning, Soundlink FROM Subject WHERE srsstage>0 """
    cursor.execute(c)
    result = cursor.fetchall()
    if len(result) > 5:
        sampleitems = sample(result, 5)
    else:
        sampleitems = fiverandomsubjects()
    return sampleitems
    pass


def fiverandomsubjects():
    c = """SELECT SID, EMeaning, GMeaning, Soundlink FROM Subject"""
    cursor.execute(c)
    result = cursor.fetchall()
    sampleitems = sample(result, 5)
    return sampleitems
    pass


def createjson(path):
    try:
        c = """SELECT Subject.SID, Subject.srsstage, Review.Date, Review.Timeswrong, Review.Timeswronginsession FROM Subject INNER JOIN Review ON Subject.SID = Review.SID"""
        cursor.execute(c)
        result = cursor.fetchall()
        dictionary = {
            "SID": [],
            "srsstage": [],
            "date": [],
            "Timeswrong": [],
            "Timeswronginsession": []
        }
        for i in result:
            dictionary["SID"].append(i[0])
            dictionary["srsstage"].append(i[1])
            dictionary["date"].append(i[2])
            dictionary["Timeswrong"].append(i[3])
            dictionary["Timeswronginsession"].append(i[4])

        filename = "/savefile" + time[0:10] +".json"
        # we neeeeed / not \ for it to work  ... rip

        with open(path + filename, "w") as outfile:

            json.dump(dictionary, outfile)

        return "Export Done!"

    except Exception as ex:
        message = "Sorry, not possible to save!\nPlease choose another directory."
        # template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        # message = template.format(type(ex).__name__, ex.args)
        return message


def updatedatabase(filename):
    try:
        reset_all_to_lessons()
        # fill in database with savefile data
        data = json.load(open(filename))
        c = """UPDATE Subject SET srsstage=? WHERE SID=?"""
        d = """INSERT OR IGNORE INTO Review(Date, Timeswrong, Timeswronginsession, SID) VALUES (?, ?, ?, ?)"""
        e = """UPDATE Review SET date=?, Timeswrong=?, Timeswronginsession=? WHERE SID=?"""
        for v in range(len(data["SID"])):
            cursor.execute(c, (data["srsstage"][v], data["SID"][v]))
            cursor.execute(d, (data["date"][v], data["Timeswrong"][v], data["Timeswronginsession"][v], data["SID"][v]))
            cursor.execute(e, (data["date"][v], data["Timeswrong"][v], data["Timeswronginsession"][v], data["SID"][v]))
        connection.commit()
        return "Import Done!"

    except:
        return "Sorry, not possible to update!\nPlease choose another file."
    # except Exception as ex:
    #     #message = "Sorry, not possible to save!\nPlease choose another directory."
    #     template = "An exception of type {0} occurred. Arguments:\n{1!r}"
    #     message = template.format(type(ex).__name__, ex.args)
    #     return message


def topboxproperties(name):
    # list of screens with their shown name and where back button will navigate
    screens = {"mainscreen": ["Home", "mainscreen"],
                "reviewscreen": ["Reviews", "mainscreen"],
                "lessonscreen": ["Lessons", "mainscreen"],
                "lessonquizscreen": ["Quiz", "lessonscreen"],
                "StatisticsScreen": ["Stats", "mainscreen"],
                "ExtrasScreen": ["Extras", "mainscreen"],
                "MemoryScreen": ["Quiz", "ExtrasScreen"],
                "QuizStatAdvancedScreen": ["Stats", "ExtrasScreen"],
                "SoundcheckScreen": ["Quiz", "ExtrasScreen"],
                "SaveScreen": ["Save", "mainscreen"],
                "TopicChoice": ["Topic", "mainscreen"],
                "Tutorial": ["Tutorial", "mainscreen"],
                "DevMode": ["Dev", "mainscreen"],
                "About": ["About", "mainscreen"]}
    return screens.get(name)


def splitmyword(word):
    # used for vocabulary that are too long for button size
    if len(word) > 14 and type(word) == str:
        if " " in word:
            word = word.replace(" ", "\n")
        else:
            word = word[:len(word)//2-1] + "\n " + word[len(word)//2-1:]
    return word


def unsplitmyword(word):
    # longer words are split in some button texts
    # but will not be recognized as correctly answered if split
    # for this, they need to transformed in their original form
    if len(word) > 14 and type(word) == str:
        if " " in word:
            word = word.replace("\n ", "")

        if "\n" in word:
            word = word.replace("\n", " ")
    return word


def hide_widget(wid, dohide=True):
    # source: https://stackoverflow.com/questions/41985573/hiding-and-showing-a-widget
    if hasattr(wid, 'saved_attrs'):
        if not dohide:
            wid.height, wid.size_hint_y, wid.opacity, wid.disabled = wid.saved_attrs
            del wid.saved_attrs
    elif dohide:
        wid.saved_attrs = wid.height, wid.size_hint_y, wid.opacity, wid.disabled
        wid.height, wid.size_hint_y, wid.opacity, wid.disabled = 0, None, 0, True


if __name__ == "__main__":
    #createjson()
    #readjson("safefile2022-09-12.json")
    #print(max(progression2())[0])
    # createjson("C:/APP/")
    # print(updatedatabase("emptydatabase.json"))
    # print(updatedatabase("filleddatabase.json"))
    #print(max(progression2())[0])
    #print(topboxproperties("DevMode"))
    #print(splitmyword("electrical Engineering"))
    print(get_item_with_emeaning("highpass"))
    pass