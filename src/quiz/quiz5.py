from emora_stdm import DialogueFlow
from emora_stdm import DialogueFlow, Macro, Ngrams
from typing import Dict, Any, List, Callable, Pattern, Tuple
import re
import time
import json
import requests
import pickle
import csv
from enum import Enum
import random
import openai
from json import JSONDecodeError

CHATGPT_MODEL = 'gpt-3.5-turbo'

VALUE_TYPE = bool | str | int | float | list | tuple | dict


class V(Enum):
    service = 0,  # str
    appointment = 1  # str


def generate(o: VALUE_TYPE) -> str:
    """
    :param o: an object to generate the regular expression for.
    :return: the regular expression for the object.
    :raise ValueError: if the object is not one of ``VALUE_TYPE``.
    """
    match o:
        case bool():
            return r'(?:true|false)'
        case str():
            return r'\".*\"'
        case int():
            return r'-?\d+'
        case float():
            f = r'(?:\.\d+)'
            return r'-?(?:\d+{}?|\d*{})'.format(f, f)
        case list():
            return generate_list(o)
        case tuple():
            return generate_tuple(o)
        case dict():
            return generate_dict(o)
        case _:
            raise TypeError(f'Invalid value type: {type(o)}.')


def generate_list(o: List[VALUE_TYPE]) -> str:
    """
    :param o: a list to generate the regular expression for. All items in the list must have the same type.
    :return: the regular expression for the list.
    :raise ValueError: if the list is empty.
    :raise TypeError: if not all items in the list have the same type.
    """
    if not o: raise ValueError(f'List must not be empty.')
    otype = type(o[0])
    if not all(isinstance(t, otype) for t in o[1:]):
        raise TypeError(f'All items in the list must have the same type: {o}.')
    v = generate(o[0])
    return r'\[(?:\s*{}(?:\s*,\s*{})*)?\s*]'.format(v, v)


def generate_tuple(o: Tuple) -> str:
    """
    :param o: a tuple to generate the regular expression for.
    :return: the regular expression for the tuple.
    :raise ValueError: if the tuple is empty.
    """
    if not o: raise ValueError(f'Tuple must not be empty.')
    ls = [r'\[']
    for i, v in enumerate(o):
        ls.append(r'(?:\s*{})?'.format(generate(v)))
        ls.append(_comma(i, len(o)))
    ls.append(r'\s*]')
    return ''.join(ls)


def generate_dict(o: Dict[str, VALUE_TYPE]) -> str:
    """
    :param o: a dictionary to generate the regular expression for. All keys in the dictionary must be strings.
    :return: the regular expression for the dictionary.
    :raise ValueError: if the dictionary is empty.
    :raise TypeError: if any key in the dictionary is not a string.
    """
    if not o: raise ValueError(f'Dictionary must not be empty.')
    ls = [r'{']
    for i, (k, v) in enumerate(o.items()):
        if not isinstance(k, str): raise TypeError
        key = r'\"{}\"'.format(k)
        ls.append(r'\s*{}\s*:\s*{}'.format(key, generate(v)))
        ls.append(_comma(i, len(o)))
    ls.append(r'\s*}')
    return ''.join(ls)


def _comma(index: int, size: int) -> str:
    """
    :param index: the index of the current item.
    :param size: the size of the collection.
    :return: the regular expressions of a comma for a delimiter in a collection.
    """
    s = r'\s*,'
    return r'(?:{})?'.format(s) if index == size - 1 else s


class MacroGPTAPPT(Macro):

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):

        if vars['service'] == 'hair cut' or 'haircut':
            content = 'Does the speaker say anything about monday at 10 AM, 1 PM, or 2 PM or tuesday at 2 PM? Accept acronyms like mon and tues. Respond in one word, True or False. speaker:' + ngrams.text()
        elif vars['service'] == 'perm':
            content = 'Does the speaker say anything about friday 10 AM, 11 AM, 1 PM, or 2 PM or saturday at 10 am or 2 PM? Accept acronyms like fri and sat. Respond in one word, True or False. speaker:' + ngrams.text()
        elif vars['service'] == 'hair color' or 'hair coloring':
            content = 'Does the speaker say anything about wednesday 10 AM, 11 AM, or 1 PM or thursday at 10 AM or 11 AM? Accept acronyms like wed and thurs. Respond in one word, True or False. speaker:' + ngrams.text()

        model = 'gpt-3.5-turbo'
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{'role': 'user', 'content': content}]
        )
        output = response['choices'][0]['message']['content'].strip()
        if output == ('True.' or 'True'):
            return True
        else:
            return False

class MacroGPTJSON(Macro):
    def __init__(self, request: str, full_ex: Dict[str, Any], empty_ex: Dict[str, Any] = None,
                 set_variables: Callable[[Dict[str, Any], Dict[str, Any]], None] = None):
        """
        :param request: the task to be requested regarding the user input (e.g., How does the speaker want to be called?).
        :param full_ex: the example output where all values are filled (e.g., {"call_names": ["Mike", "Michael"]}).
        :param empty_ex: the example output where all collections are empty (e.g., {"call_names": []}).
        :param set_variables: it is a function that takes the STDM variable dictionary and the JSON output dictionary and sets necessary variables.
        """
        self.request = request
        self.full_ex = json.dumps(full_ex)
        self.empty_ex = '' if empty_ex is None else json.dumps(empty_ex)
        self.check = re.compile(generate(full_ex))
        self.set_variables = set_variables

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        examples = f'{self.full_ex} or {self.empty_ex} if unavailable' if self.empty_ex else self.full_ex
        prompt = f'{self.request} Respond in the JSON schema such as {examples}: {ngrams.raw_text().strip()}'
        output = gpt_completion(prompt)
        if not output: return False

        try:
            d = json.loads(output)
        except JSONDecodeError:
            return False

        if self.set_variables:
            self.set_variables(vars, d)
        else:
            vars.update(d)

        return True


class MacroNLG(Macro):
    def __init__(self, generate: Callable[[Dict[str, Any]], str]):
        self.generate = generate

    def run(self, ngrams: Ngrams, vars: Dict[str, Any], args: List[Any]):
        return self.generate(vars)


def gpt_completion(input: str, regex: Pattern = None) -> str:
    response = openai.ChatCompletion.create(
        model=CHATGPT_MODEL,
        messages=[{'role': 'user', 'content': input}]
    )
    output = response['choices'][0]['message']['content'].strip()

    if regex is not None:
        m = regex.search(output)
        output = m.group().strip() if m else None

    return output


def api_key():
    PATH_API_KEY = 'resources/openai_api.txt'
    openai.api_key_path = PATH_API_KEY


def quiz5() -> DialogueFlow:
    transitions = {
        'state': 'start',
        '`Hello, how can I help you?`': {
            'state': 'service',
            '#SET_SERVICE': {
                '`A ` #GET_SERVICE `, great! What date and time are you looking for?`': {
                    '#SET_APPT': {
                        '`Your appointment is set. See you!`': 'end'
                    },
                    'error': {
                        '`Sorry, that slot is not available for a ` #GET_SERVICE `.`': {
                            'error': {
                                '`Goodbye.`': 'end'
                            }
                        }
                    }
                }
            },
            'error': {
                '`Sorry, we do not provide that service.`': {
                    'error': {
                        '`Goodbye.`': 'end'
                    }
                }
            },
        }
    }

    macros = {
        'GET_SERVICE': MacroNLG(get_service),
        'SET_SERVICE': MacroGPTJSON(
            'Is the speaker asking for hair coloring, perm, or hair cut? Convert their wording for what they\'re asking for to hair coloring, perm, or hair cut, if synonyms.',
            {V.service.name: "hair cut"}, {V.service.name: []}),
        'SET_APPT': MacroGPTAPPT()
    }

    df = DialogueFlow('start', end_state='end')
    df.load_transitions(transitions)
    df.add_macros(macros)
    return df


def get_service(vars: Dict[str, Any]):
    if V.service == False:
        return False
    ls = vars['service']
    return ls



if __name__ == '__main__':
    api_key()
    quiz5().run()
