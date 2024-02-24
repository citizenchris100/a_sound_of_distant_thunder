from Util import use_textwrap
import random
import re


def next_response(hero, score, sum, succeed):
    return dict (
        hero_responses = hero,
        score = score,
        sum = sum,
        succeed = succeed
    )

def display_dialog_choices(hero):
    print('------------------------------')
    print('------------------------------')
    for i in range(len(hero)):
        num = i + 1
        if not hero[i].used:
            print(num, ": ", hero[i].get_dialog_sum(), sep='')
    print('------------------------------')
    print('------------------------------')

def persuasion_system(character, npc, hero, responses, start):
    value = start
    while True:
        display_dialog_choices(hero)
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

def conversation_system(character, npc, hero, responses, event):
    while True:
        display_dialog_choices(hero)
        n = input(
            "Enter the number of the dialog option\n"
            "Additionally you can type \'Exit\' to return to the previous Menu.\n> ")
        print('------------------------------')
        if n.isdigit() and int(n) <= len(hero):
            m = int(n) - 1
            for i in range(len(event)):
                if event[i]["label"] == hero[m].get_dialog_sum():
                    print(character.get_name(), ": ", hero[m].get_dialog_text(), sep='')
                    hero.pop(m)
                    print(npc.get_name(), ": ", responses[m].get_dialog_text(), sep='')
                    responses.pop(m)
                    event[i]["action"](event[i]["op1"], event[i]["op1"], event[i]["op3"])
            print(character.get_name(), ": ", hero[m].get_dialog_text(), sep='')
            hero.pop(m)
            print(npc.get_name(), ": ", responses[m].get_dialog_text(), sep='')
            responses.pop(m)
        elif "exit" in n.lower():
            break
        else:
            print('------------------------------')
            print("Invalid option")