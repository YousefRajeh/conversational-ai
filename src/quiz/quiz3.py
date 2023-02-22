''' THIS CODE WAS MY OWN WORK, IT WAS WRITTEN WITHOUT CONSULTING ANY
SOURCES OUTSIDE OF THOSE APPROVED BY THE INSTRUCTOR. Yousef Rajeh'''
from emora_stdm import DialogueFlow, Macro, Ngrams
from typing import Dict, Any, List
import re


class MacroGetName(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        r = re.compile(r"(?:can|you|call|called|me|my|name|could|should|am|is|they|i|want|to|be|i'm|hey|hi|hello|\s)*("
                       r"mr|mrs|ms|dr|prof)?(?:^|\s)([a-z'-]+)(?:\s([a-z'-]+))?(?:\s[a-z'?.!]?)*?")
        m = r.search(ngrams.text())
        if m is None: return False

        title, firstname, lastname, nameFlag = None, None, None, None

        if m.group(1):
            title = m.group(1)
            if m.group(3):
                firstname = m.group(2)
                lastname = m.group(3)
                nameFlag = 'True'
            else:
                firstname = m.group()
        else:
            if m.group(3):
                firstname = m.group(2)
                lastname = m.group(3)
                nameFlag = 'True'
            else:
                firstname = m.group()


        vars['TITLE'] = title
        vars['FIRSTNAME'] = firstname
        vars['LASTNAME'] = lastname
        vars['FLAG'] = nameFlag

        return True


def quiz3() -> DialogueFlow:
    transitions = {
        'state': 'start',
        '`Hello. What should I call you?`': {
            'state': 'name',
            '#GET_NAME': {
                '#IF($FLAG=True)`It\'s nice to meet you,` $FIRSTNAME`. You\'re the first person I\'ve met called` $LASTNAME`. What was the latest movie you watched?`': {
                    'state': 'movie',
                    '[$LAST_MOVIE=#ONT(marvel)]': {
                        '`I love Marvel movies, especially ` $LAST_MOVIE `. Who is your favorite guardian of the galaxy?`': {
                            'state': 'guardians',
                            '[$CHARACTER=#ONT(gchar)]': {
                                '`So your favorite is ` $CHARACTER `?  Mine is baby groot his dance scene was so cute! So I guess you are a big fan of superhero movies?`': {
                                    '[{yes, ye, yeah, of course, certainly, yee, indeed, absolutely, sure, fine, amen, true, yea, yep, definitely, precisely, am}]': {
                                        '`That\'s great, I grew up reading their comics. What made you like them?`': {
                                            '#UNX': {
                                                '`Thanks for sharing.`': 'end'
                                            }
                                        }
                                    },
                                    'error': {
                                        '`That\'s interesting, why do you think so?`': {
                                            '#UNX': {
                                                '`Thanks for sharing.`': 'end'
                                            }
                                        }
                                    }
                                }
                            },
                            'error': {
                                '`I didn\'t get that. Could you tell me who it is again, please?`': 'guardians'
                            }
                        }
                    },
                    '[$LAST_MOVIE=#ONT(action)]': {
                        '`Top Gun: Maverick was such an exciting movie. Do you think Maverick or Rooster, is a better character?`': {
                            'state': 'topgun',
                            '[{maverick, pete, mitch, mitchell}]': {
                                '`So your favorite is Maverick? Me too, Tom Cruise\'s performance was great!! Are you a fan of action comedy movies?`': {
                                    'state': 'action',
                                    '[{yes, ye, yeah, of course, certainly, yee, indeed, absolutely, sure, fine, amen, true, yea, yep, definitely, precisely, am}]': {
                                        '`That\'s great, it\'s a fun genre of film, my favorites are jackie chans\' films. What made you like them?`': {
                                            '#UNX': {
                                                '`Thanks for sharing.`': 'end'
                                            }
                                        }
                                    },
                                    'error': {
                                        '`That\'s interesting, why do you think so?`': {
                                            '#UNX': {
                                                '`Thanks for sharing.`': 'end'
                                            }
                                        }
                                    }
                                }
                            },
                            '[{rooster, brad, bradley, bradshaw}]': {
                                '`So your favorite is Rooster? Mine is Maverick, Tom Cruise\'s performance was great!! Are you a fan of action movies?`': 'action'
                            },
                            'error': {
                                '`I didn\'t get that. Could you tell me who it is again, please?`': 'topgun'
                            }
                        }
                    },
                    '[$LAST_MOVIE=#ONT(comedy)]': {
                        '`The nice guys is such a funny film. Do you think Jackson or Holland, is a better character?`': {
                            'state': 'niceguy',
                            '[$CHARACTER=[{jackson, jack, jackey, healy}]]': {
                                '`So your favorite is Jack? Mine is Holland, Ryan Gosling\'s performance was great! Are you a fan of comedy movies?`': {
                                    'state': 'comedy',
                                    '[{yes, ye, yeah, of course, certainly, yee, indeed, absolutely, sure, fine, amen, true, yea, yep, definitely, precisely, am}]': {
                                        '`I love watching comedy films too, they are great with family too. What made you like them?`': {
                                            '#UNX': {
                                                '`Thanks for sharing.`': 'end'
                                            }
                                        }
                                    },
                                    'error': {
                                        '`That\'s interesting, why do you think so?`': {
                                            '#UNX': {
                                                '`Thanks for sharing.`': 'end'
                                            }
                                        }
                                    }
                                }
                            },
                            '[{holland, march}]': {
                                '`Mine is Holland, Ryan Gosling\'s performance was great! Are you a fan of comedy movies??`': 'comedy'
                            },
                            'error': {
                                '`I didn\'t get that. Could you tell me who it is again, please?`': 'niceguy'
                            }
                        }
                    },
                    '[$LAST_MOVIE=#ONT(scifi)]': {
                        '`Tenet is such a confusing movie, I didn\'t get it. Do you think Neil or Kat, is a better character?`': {
                            'state': 'scifi',
                            '[$CHARACTER=[{neil}]]': {
                                '`So your favorite is Neil? Me too, Robert Pattinson\'s performance was great! Are you a fan of Sci-Fi movies?`': {
                                    'state': 'tenet',
                                    '[{yes, ye, yeah, of course, certainly, yee, indeed, absolutely, sure, fine, amen, true, yea, yep, definitely, precisely, am}]': {
                                        '`I love watching Sci-Fi films too, my favourite is star wars. What made you like them?`': {
                                            '#UNX': {
                                                '`Thanks for sharing.`': 'end'
                                            }
                                        }
                                    },
                                    'error': {
                                        '`That\'s interesting, why do you think so?`': {
                                            '#UNX': {
                                                '`Thanks for sharing.`': 'end'
                                            }
                                        }
                                    }
                                }
                            },
                            '[{kat}]': {
                                '`So your favorite is Kat? Robert Pattinson\'s performance was great! Are you a fan of Sci-Fi movies?`': 'tenet'
                            },
                            'error': {
                                '`I didn\'t get that. Could you tell me who it is again, please?`': 'scifi'
                            }
                        }
                    },
                    '[$LAST_MOVIE=#ONT(horror)]': {
                        '`I think ` $LAST_MOVIE ` is a modern twist on horror movies. Do you think Tess or Keith, is a better character?`': {
                            'state': 'horror',
                            '[$CHARACTER=[{tess}]]': {
                                '`So your favorite is Tess? Me too, Georgina Campbell\'s performance was great! Are you a fan of Horror movies?`': {
                                    'state': 'barbarian',
                                    '[{yes, ye, yeah, of course, certainly, yee, indeed, absolutely, sure, fine, amen, true, yea, yep, definitely, precisely, am}]': {
                                        '`I love watching Horror films too, especially during Halloween. What made you like them?`': {
                                            '#UNX': {
                                                '`Thanks for sharing.`': 'end'
                                            }
                                        }
                                    },
                                    'error': {
                                        '`That\'s interesting, why do you think so?`': {
                                            '#UNX': {
                                                '`Thanks for sharing.`': 'end'
                                            }
                                        }
                                    }
                                }
                            },
                            '[{keith}]': {
                                '`So your favorite is Keith? Mine is Tess, Georgina Campbell\'s performance was great! Are you a fan of Horror movies?`': 'barbarian'
                            },
                            'error': {
                                '`I didn\'t get that. Could you tell me who it is again, please?`': 'horror'
                            }
                        }
                    },
                    '[$LAST_MOVIE=#ONT(romance)]': {
                        '`I think `$LAST_MOVIE` is a great romantic film. Do you think David or Georgia, is a better character?`': {
                            'state': 'romance',
                            '[$CHARACTER=[{david, guy, man, husband}]]': {
                                '`So your favorite is David? Me too, George Clooney\'s performance was great! Are you a fan of romantic movies?`': {
                                    'state': 'tick',
                                    '[{yes, ye, yeah, of course, certainly, yee, indeed, absolutely, sure, fine, amen, true, yea, yep, definitely, precisely, am}]': {
                                        '`I love watching romantic films too, especially during Valentine\'s day. What made you like them?`': {
                                            '#UNX': {
                                                '`Thanks for sharing.`': 'end'
                                            }
                                        }
                                    },
                                    'error': {
                                        '`That\'s interesting, why do you think so?`': {
                                            '#UNX': {
                                                '`Thanks for sharing.`': 'end'
                                            }
                                        }
                                    }
                                }
                            },
                            '[{georgia, girl, woman, wife}]': {
                                '`So your favorite is Georgia? Mine is David, George Clooney\'s performance was great! Are you a fan of romantic movies?`': 'tick'
                            },
                            'error': {
                                '`I didn\'t get that. Could you tell me who it is again, please?`': 'romance'
                            }
                        }
                    },
                    'score': 0.5,
                    'error': {
                        '`I\'m not sure if I know that one. Could you tell the name of another movie you\'ve seen, please?`': 'movie'
                    }
                },
                'score': 0.5,
                '`It\'s nice to meet you,` $FIRSTNAME`. You\'re the first person I\'ve met called` $FIRSTNAME`. What was the latest movie you watched?`': 'movie'
            },
            'error': {
                '`I didn\'t get that. Could you tell me it again, please?`': 'name'
            }
        }
    }

    macros = {
        'GET_NAME': MacroGetName()
    }

    df = DialogueFlow('start', end_state='end')
    df.knowledge_base().load_json_file('resources/ontology_quiz3.json')
    df.load_transitions(transitions)
    df.add_macros(macros)
    return df

if __name__ == '__main__':
    quiz3().run()
