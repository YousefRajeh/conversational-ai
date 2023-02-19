''' THIS CODE WAS MY OWN WORK, IT WAS WRITTEN WITHOUT CONSULTING ANY
SOURCES OUTSIDE OF THOSE APPROVED BY THE INSTRUCTOR. Yousef Rajeh'''
from emora_stdm import DialogueFlow, Macro, Ngrams
from typing import Dict, Any, List
import re


class MacroGetName(Macro):
    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        r = re.compile(r"(?:can|you|call|called|me|my|name|should|am|is|they|i|want|to|be|i'm|hey|hi|hello|\s)*("
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
                            '[$CHARACTER=#ONT(guardians of the galaxy)]': {
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
                    'error': {
                        '`I\'m not sure if I know that one. Could you tell the name of another movie you\'ve seen, please?`': 'movie'
                    }
                } ,
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
