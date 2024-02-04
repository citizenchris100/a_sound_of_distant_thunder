from Util import use_textwrap
import random


def next_response(hero, score, sum, succeed):
    return dict (
        hero_responses = hero,
        score = score,
        sum = sum,
        succeed = succeed
    )

def dialog_system(character, npc, hero, responses, start):
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
            m = int(n) - 1
            print('------------------------------')
            hero[m].set_dialog_used(True)
            print(character.get_name() , ": " , hero[m].get_dialog_text(), sep='')
            if random.randint(0, 12) - (character.get_charm_attribute() / 2) < value - hero[m].get_dialog_agro():
                print('------------------------------')
                print(npc.get_name() , ": " , responses["good"].get_dialog_text(), sep='')
                return next_response(responses["good"].get_responses(), start - (character.get_charm_attribute() / 2),
                                     hero[m].get_dialog_sum(), True)
            else:
                print('------------------------------')
                print(npc.get_name(), ":", responses["bad"].get_dialog_text(), sep='')
                return next_response(responses["bad"].get_responses(), start + random.randint(0, 6),
                                     hero[m].get_dialog_sum(), False)
        elif "exit" in n.lower():
            break
        else:
            print('------------------------------')
            print("Invalid option")
