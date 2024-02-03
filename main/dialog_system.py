from Util import use_textwrap
import random


def next_response(hero,score, val):
    return dict (
        hero_responses = hero,
        score = score,
        val = val
    )

def dialog_system(hero, responses, character, start):
    value = start
    while True:
        print('------------------------------')
        print('------------------------------')
        for i in range(len(hero)):
            num = i + 1
            if not hero[i].used:
                print(num, ": ", hero[i].get_dialog_sum(), sep='')
        print('------------------------------')
        print('------------------------------')
        n = input(
            "Enter the number of the dialog option\n"
            "Additionally you can type \'Exit\' to return to the previous Menu.\n> ")
        if n.isdigit() and int(n) <= len(hero):
            print('------------------------------')
            use_textwrap(hero[i].get_dialog_text())
            hero[i].set_dialog_used(True)
            use_textwrap(hero[i].get_dialog_text())
            if random.randint(0, 12) - character.get_charm_attribute() < value + hero[i].get_dialog_agro():
                use_textwrap(responses["good"].get_dialog_text())
                return next_response(responses["good"].get_good_responses(), start + character.get_charm_attribute(), True)
            else:
                use_textwrap(responses["bad"].get_dialog_text())
                return next_response(responses["bad"], start + random.randint(0, 6), False)
