''' THIS CODE WAS MY OWN WORK, IT WAS WRITTEN WITHOUT CONSULTING ANY
SOURCES OUTSIDE OF THOSE APPROVED BY THE INSTRUCTOR. Yousef Rajeh'''
from emora_stdm import DialogueFlow, Macro, Ngrams
from typing import Dict, Any, List
import re
import time
import json
import requests
import  pickle
import csv
import random

fhandle = open('resources/songlist.csv')
song_dict=dict()
movies_dict=dict()
rec_set = set()
for line in fhandle:
    words = line.split(',')
    song_dict.update({words[0]: dict()})
    n = len(words)
    for i in range(1, n-1, 2):
        if words[0] in song_dict.keys():
            song_dict[words[0]].update({words[i]:words[i + 1]})

with open('resources/movieslist.csv', encoding="utf8", mode='r') as infile:
    reader = csv.reader(infile)
    movies_dict = {rows[0]:rows[1] for rows in reader}


def save(df: DialogueFlow, varfile: str):
    d = {k: v for k, v in df.vars().items() if not k.startswith('_')}
    pickle.dump(d, open(varfile, 'wb'))


def load(df: DialogueFlow, varfile: str):
    d = pickle.load(open(varfile, 'rb'))
    df.vars().update(d)
    df.run()
    save(df, varfile)


class MacroRecMovie(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global rec_set
        while 1:
            key, value = random.choice(list(movies_dict.items()))
            if key not in rec_set:
                break
        rec_set.add(key)
        vars[vars['SFIRSTNAME']] = key
        return "How about watching " + key + "?"

class MacroSongInfo(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        for song_auth, song_genre in song_dict[vars[vars['SFIRSTNAME']]].items():
            return vars[vars['SFIRSTNAME']] + " is a song by " + song_auth + " in the genre of " + song_genre

class MacroRecSong(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        global rec_set
        while 1:
            key, value = random.choice(list(song_dict.items()))
            if key not in rec_set:
                break
        rec_set.add(key)
        vars[vars['SFIRSTNAME']] = key
        return "How about listening to " + key + "?"

class MacroMovieInfo(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        return "Here is an overview: " + movies_dict[vars[vars['SFIRSTNAME']]]



class MacroGreeting(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[str]):
        current_time = time.strftime("%H")
        int_time = int("{}".format(current_time))
        time_phrase = "Good "
        if int_time < 11:
            time_phrase += "Morning"
        elif int_time < 16:
            time_phrase += "Afternoon"
        else:
            time_phrase += "Evening"
        url = 'https://api.weather.gov/gridpoints/FFC/52,88/forecast'
        r = requests.get(url)
        d = json.loads(r.text)
        periods = d['properties']['periods']
        today = periods[0]
        weather = today['shortForecast']

        vn = 'Greeting'
        if vn not in vars:
            vars[vn] = 1
            return time_phrase + "; it's " + weather + " today. "+ "What's your name?"
        else:
            count = vars[vn] + 1
            vars[vn] = count
            match count%10:
                case 2:
                    return time_phrase + "; it's " + weather + " today. "+ "What should I call you?"
                case 3:
                    return time_phrase + "; it's " + weather + " today. "+ "Can I have your name?"
                case 4:
                    return time_phrase + "; it's " + weather + " today. "+ "What would your name be?"
                case 5:
                    return time_phrase + "; it's " + weather + " today. "+ "What can I call you?"
                case 6:
                    return time_phrase + "; it's " + weather + " today. "+ "How can I address you?"
                case 7:
                    return time_phrase + "; it's " + weather + " today. "+ "What are you named?"
                case 8:
                    return time_phrase + "; it's " + weather + " today. "+ "What do you call yourself?"
                case 9:
                    return time_phrase + "; it's " + weather + " today. "+ "What does everyone call you?"
                case 0:
                    return time_phrase + "; it's " + weather + " today. "+ "May I ask you what your name is?"
                case 1:
                    return time_phrase + "; it's " + weather + " today. "+ "Could you give me your name?"







class MacroGetName(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        r = re.compile(r"(?:can|call|called|me|my|name|could|should|am|is|they|i|want|to|be|hey|hi|hello|how|are|you|\s)*("
                       r"mr|mrs|ms|dr|prof)?(?:^|\s)([a-z'-]+)(\s([a-z'-]+))?(?:\s[a-z'?.!]?)*?")
        m = r.search(ngrams.text())
        if m is None: return False

        title, firstname, lastname, recFlag = None, None, None, None

        if m.group(1):
            title = m.group(1)
            if m.group(3):
                firstname = m.group(2)
                lastname = m.group(3)
            else:
                firstname = m.group()
        else:
            if m.group(3):
                firstname = m.group(2)
                lastname = m.group(3)
            else:
                firstname = m.group()


            if firstname in vars:
                rec = vars[firstname]
                if rec in song_dict.keys():
                    vars['RECGREET'] = "Welcome back, " + firstname + ". Did you listen to " + rec + "?"
                    recFlag = 'True'
                elif rec in movies_dict.keys():
                    vars['RECGREET'] = "Welcome back, " + firstname + ". Did you watch " + rec + "?"
                    recFlag = 'True'
            else:
                vars['RECGREET'] = "Hello, " + firstname + ". It's nice to meet you. What do you want me to recommend?"
                recFlag = 'False'


        vars['TITLE'] = title
        vars['SFIRSTNAME'] = firstname
        vars['LASTNAME'] = lastname
        vars['FLAG'] = recFlag

        return True


def quiz4() -> DialogueFlow:
    transitions = {
        'state': 'start',
        '#GREETING': {
            'state': 'name',
            '#GET_NAME': {
                '#IF($FLAG=False) $RECGREET': {
                    'state': 'newrec',
                    '[{#LEM(movie), #LEM(film)}]': 'movie',
                    '[{#LEM(music), #LEM(song)}]': 'song',
                    'score': 0.5,
                    'error': {
                        '`I\'m not sure if I can do that. I can only recommend movies and songs.`': 'newrec'
                    }
                },
                '#IF($FLAG=True) $RECGREET': {
                    '[{interesting,funny,wonderful,great,fun,like,liked,loved,yes, ye,yup, yeah, of course, certainly, yee, indeed, absolutely, sure, fine, amen, true, yea, yep, definitely, precisely, am}]': {
                        '`That\'s great! What else do you want me to recommend?`': 'newrec'
                    },
                    'error': {
                        '`That\'s interesting, I hope my next recommendation is better! Would you like a song or a movie?`': 'newrec'
                        }
                }
            },
            'error': {
                '`I didn\'t get that. Could you tell me it again, please?`': 'name'
            }
        }
    }


    song_transitions = {
        'state': 'song',
        '#REC_SONG': {
            'state': 'SongFeed',
            '[{listen,ok,okay,yes, ye, yeah, of course, certainly, yee, indeed, absolutely, sure, fine, amen, true, yea, yep, definitely, precisely}]': {
                '`That\'s great! Enjoy.`': 'end'
            },
            '[{already, another, else, other, recommend, recommendation, something, change, different}]': 'song',
            '[{who, why, what, how, when, where, about}]': {
                '#SONG_INFO': 'SongFeed'
            },
            'error': 'song'
        }
    }

    movie_transitions = {
        'state': 'movie',
        '#REC_MOVIE': {
            'state': 'movFeed',
            '[{watch,ok,okay,yes, ye, good, nice, wonderful, great, thank, thanks, alright, yeah, of course, certainly, yee, indeed, absolutely, sure, fine, amen, true, yea, yep, definitely, precisely}]': {
                '`That\'s great! Enjoy.`': 'end'
            },
            '[{already, another, else, other, recommend, recommendation, something, change, different}]': 'movie',
            '[{who, why, what, how, when, where, about}]': {
                '#MOVIE_INFO': 'movFeed'
            },
            'error': 'movie'
        }
    }

    macros = {
        'GET_NAME': MacroGetName(),
        'GREETING': MacroGreeting(),
        'REC_MOVIE': MacroRecMovie(),
        'MOVIE_INFO': MacroMovieInfo(),
        'REC_SONG': MacroRecSong(),
        'SONG_INFO': MacroSongInfo()
    }

    df = DialogueFlow('start', end_state='end')
    df.load_transitions(transitions)
    df.load_transitions(song_transitions)
    df.load_transitions(movie_transitions)
    df.add_macros(macros)


    return df


if __name__ == '__main__':
    load(quiz4(), 'resources/names.pkl')