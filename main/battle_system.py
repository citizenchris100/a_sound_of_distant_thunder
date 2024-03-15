import random
import math
from inventory import inventory
from inventory import loot_add
from lvl_system import level_up


# TODO: improve combat verbiage by implementing some kind of random library

def display_score():
    file = open("../score.txt", "r")
    for line in file:
        xline = line.split(",")
        print(xline[0], xline[1])
    exit()


def write_score(score, name):
    file = open("../score.txt", "a")
    file.write(str(name))
    file.write(",")
    file.write(str(score))
    file.write(",")
    file.write("\n")
    file.close()


def game_over(character_var):
    score = character_var.exp
    if character_var.hp < 1:
        print("You have been defeated.")
        print("You Final score is ", score, sep='')
        name = input("Enter your Name : ")
        write_score(score, name)
        display_score()


def enemy_attack(character_var, enemy_var, hit_enemy, range):
    if hit_enemy == "yes":
        print('------------------------------')
        print(enemy_var.get_name(), "'s health is now ", enemy_var.get_health(), ".", sep='')
        print("Your current Health is ", character_var.get_health_points(), "/", character_var.get_hp_limit(), sep='')
    elif hit_enemy == "no":
        print('------------------------------')
        print("You did not hit the ", enemy_var.get_name(), ".", sep='')
        print('------------------------------')
        print("Your current Health is ", character_var.get_health_points(), "/", character_var.get_hp_limit(), sep='')
    elif hit_enemy == "surprise":
        print('------------------------------')
        print("Out of nowhere you were blindsided by an attack.")
    if "Goblin" in enemy_var.get_name() or enemy_var.get_equipped_gun() is None:
        total_attack = enemy_melee_attack(character_var, enemy_var, hit_enemy)
    else:
        if enemy_var.get_equipped_gun().get_ammo() > 0:
            if range:
                bonus = 0
            else:
                bonus = 3
            if hit_enemy == "yes":
                print('------------------------------')
                print("They return fire.")
            else:
                print('------------------------------')
                print("They fire at you with their gun.")
            if random.randint(0, 6) - bonus < enemy_var.get_luck():
                hit = (enemy_var.get_gun_skill() + enemy_var.get_equipped_gun().get_item_value())
                enemy_var.get_equipped_gun().set_ammo(enemy_var.get_equipped_gun().get_ammo() - 1)
            else:
                print("Fortunately they missed.")
                enemy_var.get_equipped_gun().set_ammo(enemy_var.get_equipped_gun().get_ammo() - 1)
                hit = 0
            defend = character_defence(character_var)
            total_attack = math.floor(hit - defend)
        else:
            total_attack = enemy_melee_attack(character_var, enemy_var, hit_enemy)
    if character_var.get_equipped_armour() is not None:
        character_var.get_equipped_armour.set_item_value(character_var.get_equipped_armour.get_item_value()
                                                         - total_attack)
        if character_var.get_equipped_armour.get_item_value() > 0:
            print('------------------------------')
            print("Your armour has been damaged. \n")
        else:
            print('------------------------------')
            print("Your armour is no longer effective.\nYou should probably equip new armour ASAP.")
    character_var.set_health_points(character_var.get_health_points() - total_attack)
    if character_var.hp > 0:
        print('------------------------------')
        print("Your current Health is now ", character_var.get_health_points(), "/", character_var.get_hp_limit(), sep='')
    else:
        game_over(character_var)


def character_defence(character_var):
    if character_var.get_equipped_armour() is not None:
        defend = character_var.get_equipped_armour().get_item_value() + character_var.get_defence_points()
    else:
        defend = character_var.get_defence_points()
    return defend


def enemy_melee_attack(character_var, enemy_var, hit_enemy):
    if hit_enemy == "yes":
        print('------------------------------')
        print("They were able to strike back with a melee attack")
    else:
        print('------------------------------')
        print("They hit you with a melee attack")
    if "Goblin" in enemy_var.get_name() or enemy_var.get_equipped_melee() is None:
        hit = enemy_var.get_strength()
    else:
        hit = (enemy_var.get_strength() + enemy_var.get_equipped_melee().get_item_value())
    defend = character_defence(character_var)
    return math.floor(hit - defend)


def enemy_defeat(character_var, enemy_var):
    chance = random.randint(0, 10)
    if "Goblin" in enemy_var.get_name():
        if chance < character_var.get_luck():
            exp = math.ceil(enemy_var.get_strength() + random.randint(0, 10))
        else:
            exp = enemy_var.get_strength()
        print('------------------------------')
        print("You killed the ", enemy_var.name, ".", sep='')
    else:
        if enemy_var.get_gun_skill() < enemy_var.get_strength():
            if chance < character_var.get_luck():
                exp = math.ceil(enemy_var.get_strength() + random.randint(0, 10))
            else:
                exp = enemy_var.get_strength()
        else:
            if chance < character_var.get_luck():
                exp = math.ceil(enemy_var.get_gun_skill() + random.randint(0, 10))
            else:
                exp = enemy_var.get_gun_skill()
        print('------------------------------')
        print("You killed ", enemy_var.name, ".", sep='')
    print('------------------------------')
    print("You gained ", exp, " experience points.", sep='')
    character_var.set_exp(character_var.get_exp() + exp)
    level_up(character_var)


def check_ammo(character_var):
    return [item for item in character_var.get_inventory() if item.attribute == "ammo"]


def use_ammo(character_var, shots):
    for i, item in enumerate(character_var.get_inventory()):
        if item.attribute == "ammo":
            character_var.get_inventory()[i].set_item_value((character_var.get_inventory()[i].get_item_value() - shots))
            return character_var.get_inventory()[i].get_item_value()


def battle_state(character_var, enemy_var, surprise, range):
    if surprise:
        enemy_attack(character_var, enemy_var, "surprise", range)
    this_range = range
    while enemy_var.get_health() > 0:
        print('------------------------------')
        option = input("1. Melee Attack \n2. Gun Attack\n3. Inventory\n4. Flee\n> ")
        if "melee" in option.lower() or option == "1":
            bonus = 0
            sa = False
            if this_range:
                if (random.randint(0, 12) - character_var.get_stealth_attribute() < random.randint(0, 6) +
                        enemy_var.get_awareness()):
                    bonus = random.randint(0, 6) + character_var.get_strength_attribute()
                    sa = True
                    this_range = False
            if character_var.get_equipped_melee() is not None and character_var.get_equipped_melee().get_item_value() > 0:
                print('------------------------------')
                if sa:
                    print('You managed to approach and attack the enemy without being detected.')
                else:
                    print("You swing your ", character_var.get_equipped_melee().get_item_name(), " attacking the ",
                          enemy_var.get_name(), ".", sep='')

                hit = (character_var.get_strength_attribute() + character_var.get_equipped_melee().get_item_value()
                       + bonus)
                character_var.get_equipped_melee().set_item_value(character_var.get_equipped_melee().get_item_value() - 1)
                print('------------------------------')
                print("The use of your edged weapon has caused it to grow more dull")
            elif character_var.get_equipped_melee().get_item_value() <= 0:
                print('Your edged weapon is too dull to be effective. It\'s probably a good idea to replace it')
            else:
                print('------------------------------')
                if sa:
                    print('You managed to approach and attack the enemy without being detected.')
                else:
                    print("You punch the ", enemy_var.get_name(), ".", sep='')
                hit = character_var.get_strength_attribute() + bonus
            npc_attack_damage(enemy_var, (math.floor(hit - npc_defence(enemy_var))))
            if enemy_var.get_health() > 0:
                enemy_attack(character_var, enemy_var, "yes", False)
            else:
                enemy_defeat(character_var, enemy_var)
                loot_add(character_var, enemy_var)
                break
        elif "gun" in option.lower() or option == "2":
            if character_var.get_equipped_gun() is not None:
                bonus = 0
                sa = False
                if this_range:
                    if (random.randint(0, 12) - character_var.get_gun_skill() < random.randint(0, 6) +
                            enemy_var.get_awareness()):
                        bonus = random.randint(0, 6) + character_var.get_gun_skill()
                        sa = True
                else:
                    bonus = 5
                if character_var.get_equipped_gun().get_ammo() > 0:
                    print('------------------------------')
                    if sa:
                        print('You managed to approach and attack the enemy without being detected.')
                    else:
                        print("You fired your ", character_var.get_equipped_gun().get_item_name(), " attacking the ",
                              enemy_var.name, ".", sep='')
                    if random.randint(0, 6) - bonus < character_var.get_luck():
                        if random.randint(0, 12) - bonus < character_var.get_luck():
                            print("You managed to get two hits")
                            hit = use_firearm(character_var, 2)
                        else:
                            hit = use_firearm(character_var, 1)
                        npc_attack_damage(enemy_var, (math.floor(hit - npc_defence(enemy_var))))
                        if enemy_var.get_health() > 0:
                            enemy_attack(character_var, enemy_var, "yes", range)
                        else:
                            enemy_defeat(character_var, enemy_var)
                            loot_add(character_var, enemy_var)
                            break
                    else:
                        character_var.get_equipped_gun().set_ammo(character_var.get_equipped_gun().get_ammo() - 1)
                        print("You have ", character_var.get_equipped_gun().get_ammo(), " shots remaining", sep='')
                        enemy_attack(character_var, enemy_var, "no")
                else:
                    print('------------------------------')
                    print("You are out of ammo.")
            else:
                print('------------------------------')
                print("You do not have a gun equipped.\nCheck your Inventory for any available guns to equip.")
        elif option == "4":
            if random.randint(0, 6) + character_var.get_luck() > 12:
                print("You escape battle with the ", enemy_var.name, ".", sep='')
                break
            else:
                new_hp = enemy_var.get_health() - character_var.get_strength_attribute()
                character_var.set_health_points(new_hp)
                print("You were unable to escape battle. \nHowever the ", enemy_var.name,
                      " was able to strike you.", sep='')
                if character_var.get_health_points() > 0:
                    print("Your current Health is ", character_var.get_health_points(), "/", character_var.get_hp_limit(), sep='')
                else:
                    game_over(character_var)
        elif option == "3":
            inventory(character_var)
            enemy_attack(character_var, enemy_var, "no", range)
        else:
            print("Option not allowed please choose either 1, 2 or 3.")
    print("Your current Score is ", character_var.get_exp(), sep='')
    print("Your current Health is ", character_var.get_health_points(), "/", character_var.get_hp_limit(), sep='')


def npc_attack_damage(enemy_var, total_attack):
    if ("Goblin" not in enemy_var.get_name()
            and enemy_var.get_equipped_armour() is not None
            and enemy_var.get_equipped_armour().get_item_value() > 0):
        enemy_var.get_equipped_armour().set_item_value((enemy_var.get_equipped_armour().
                                                        get_item_value() - total_attack))
    enemy_var.set_health(enemy_var.get_health() - total_attack)


def npc_defence(enemy_var):
    if "Goblin" in enemy_var.get_name() or enemy_var.get_equipped_armour() is None:
        defend = enemy_var.get_defence()
    else:
        defend = enemy_var.get_defence() + enemy_var.get_equipped_armour().get_item_value()
    return defend


def use_firearm(character_var, shots):
    character_var.get_equipped_gun().set_ammo(character_var.get_equipped_gun().get_ammo() - shots)
    print("You have ", character_var.get_equipped_gun().get_ammo(), " shots remaining", sep='')
    return ((character_var.get_equipped_gun().get_item_value() + character_var.get_gun_skill())
           * shots)



