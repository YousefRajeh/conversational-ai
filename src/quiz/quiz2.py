from emora_stdm import DialogueFlow


def quiz2() -> DialogueFlow:
    transitions = {
        'state': 'start',
        '`Hello, how can I help you?`': {
            '[{haircut, hair cut}]': {
                '`A haircut, great! What date and time are you looking for?`': {
                    '[{[monday, 10 am], [monday, 1 pm], [monday, 2 pm], [tuesday, 2 pm]}]': {
                        '`Your appointment is set. See you!`': 'end'
                    },
                    'error': {
                        '`Sorry, that slot is not available for a haircut.`': {
                            'error': {
                                '`Goodbye.`': 'end'
                            }
                        }
                    }
                }
            },
            '[{hair coloring, hair color, haircolor, hair colouring}]': {
                '`Hair coloring, great! What date and time are you looking for?`': {
                    '[{[wednesday, 10 am], [wednesday, 11 am], [wednesday, 1 pm], [thursday, 10 am], [thursday 11, '
                    'am]}]': {
                        '`Your appointment is set. See you!`': 'end'
                    },
                    'error': {
                        '`Sorry, that slot is not available for hair coloring.`': {
                            'error': {
                                '`Goodbye.`': 'end'
                            }
                        }
                    }
                }
            },
            '[{perm, perms}]': {
                '`A Perm, great! What date and time are you looking for?`': {
                    '[{[friday, 10 am], [friday, 11 am], [friday, 1 pm], [friday, 2 pm], [saturday, 10 am], '
                    '[saturday, 2 pm]}]': {
                        '`Your appointment is set. See you!`': 'end'
                    },
                    'error': {
                        '`Sorry, that slot is not available for a perm.`': {
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

    df = DialogueFlow('start', end_state='end')
    df.load_transitions(transitions)
    return df


if __name__ == '__main__':
    quiz2().run()
