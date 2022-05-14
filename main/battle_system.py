import random
import math
from inventory import inventory
from inventory import loot_add
from lvl_system import level_up


# TODO: improve combat verbiage
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


def enemy_attack(character_var, enemy_var, hit_enemy):
    if hit_enemy == "yes":
        print(enemy_var.get_name(), "'s health is now ", enemy_var.get_health(), ".", sep='')
    elif hit_enemy == "no":
        print("You did not hit the ", enemy_var.get_name(), ".", sep='')
    elif hit_enemy == "surprise":
        print("Out of nowhere you were blindsided by an attack.")
    if "Goblin" in enemy_var.get_name() or enemy_var.get_equipped_gun() is None:
        total_attack = enemy_melee_attack(character_var, enemy_var, hit_enemy)
    else:
        if enemy_var.get_equipped_gun().get_ammo() > 0:
            if hit_enemy == "yes":
                print("They were able to strike back with their fire arm")
            else:
                print("They fire at you with their gun.")
            if random.randint(0, 12) < enemy_var.get_luck():
                hit = ((enemy_var.get_gun_skill() + enemy_var.get_equipped_gun().get_item_value()) * 2)
                enemy_var.get_equipped_gun().set_ammo(enemy_var.get_equipped_gun().get_ammo() - 2)
            elif random.randint(0, 6) < enemy_var.get_luck():
                hit = (enemy_var.get_gun_skill() + enemy_var.get_equipped_gun().get_item_value())
                enemy_var.get_equipped_gun().set_ammo(enemy_var.get_equipped_gun().get_ammo() - 1)
            else:
                print("Fortunately they missed.")
                enemy_var.get_equipped_gun().set_ammo(enemy_var.get_equipped_gun().get_ammo() - 1)
                hit = 0
            if character_var.get_equipped_armour() is not None:
                defend = character_var.get_equipped_armour()
            else:
                defend = 1
            total_attack = math.floor(hit / defend)
        else:
            total_attack = enemy_melee_attack(character_var, enemy_var, hit_enemy)
    if character_var.get_equipped_armour() is not None:
        character_var.get_equipped_armour.set_item_value(character_var.get_equipped_armour.get_item_value()
                                                         - total_attack)
        if character_var.get_equipped_armour.get_item_value() > 0:
            print("Your armour has been damaged. \n")
        else:
            print("Your armour is no longer effective.\nYou should probably equip new armour ASAP.")
    character_var.set_health_points(character_var.get_health_points() - total_attack)
    if character_var.hp > 0:
        print("Your health is now ", character_var.get_health_points(), ".", sep='')
    else:
        game_over(character_var)


def enemy_melee_attack(character_var, enemy_var, hit_enemy):
    if hit_enemy == "yes":
        print("They were able to strike back with a melee attack")
    else:
        print("They hit you with a melee attack")
    if "Goblin" in enemy_var.get_name() or enemy_var.get_equipped_melee() is None:
        hit = enemy_var.get_strength()
    else:
        hit = (enemy_var.get_strength() + enemy_var.get_equipped_melee().get_item_value())
    defend = character_var.get_defence_points()
    return math.floor(hit / defend)


def enemy_defeat(character_var, enemy_var):
    chance = random.randint(0, 10)
    if "Goblin" in enemy_var.get_name():
        if chance < character_var.get_luck_attribute():
            exp = math.ceil(enemy_var.get_strength() + random.randint(0, 10))
        else:
            exp = enemy_var.get_strength()
        print("You killed the ", enemy_var.name, ".", sep='')
    else:
        if enemy_var.get_gun_skill() < enemy_var.get_strength():
            if chance < character_var.get_luck_attribute():
                exp = math.ceil(enemy_var.get_strength() + random.randint(0, 10))
            else:
                exp = enemy_var.get_strength()
        else:
            if chance < character_var.get_luck_attribute():
                exp = math.ceil(enemy_var.get_gun_skill() + random.randint(0, 10))
            else:
                exp = enemy_var.get_gun_skill()
        print("You killed ", enemy_var.name, ".", sep='')
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


def battle_state(character_var, enemy_var, surprise):
    if surprise:
        enemy_attack(character_var, enemy_var, "surprise")
    while enemy_var.get_health() > 0:
        option = input("1. Melee Attack \n2. Gun Attack\n3. Inventory\n4. Flee\n> ")
        # TODO: update melee combat
        if option == "1":
            if character_var.get_equipped_melee() is not None:
                print("You swing your ", character_var.get_equipped_melee.get_item_name(), " attacking the ",
                      enemy_var.get_name(), ".", sep='')
                hit = (character_var.get_strength_attribute() + character_var.get_equipped_melee.get_item_value())
            else:
                print("You punch the ", enemy_var.get_name(), ".", sep='')
                hit = character_var.get_strength_attribute()
            defend = enemy_var.get_defence()
            enemy_var.set_health(enemy_var.get_health - (math.floor(hit / defend)))
            if enemy_var.get_health() > 0:
                enemy_attack(character_var, enemy_var, "yes")
            else:
                enemy_defeat(character_var, enemy_var)
                loot_add(character_var, enemy_var)
                break
        elif option == "2":
            if character_var.get_equipped_gun() is not None:
                if character_var.get_equipped_gun().get_ammo() > 0:
                    print("You fired your ", character_var.get_equipped_gun().get_item_name(), " attacking the ",
                          enemy_var.name, ".", sep='')
                    if random.randint(0, 6) < character_var.get_luck_attribute():
                        if random.randint(0, 12) < character_var.get_luck_attribute():
                            print("You managed to get two hits")
                            hit = ((character_var.get_equipped_gun().get_item_value() + character_var.get_gun_skill())
                                   * 2)
                            character_var.get_equipped_gun().set_ammo(character_var.get_equipped_gun().get_ammo() - 2)
                            print("You have ", character_var.get_equipped_gun().get_ammo(), " shots remaining", sep='')
                        else:
                            hit = (character_var.get_equipped_gun().get_item_value() + character_var.get_gun_skill())
                            character_var.get_equipped_gun().set_ammo(character_var.get_equipped_gun().get_ammo() - 1)
                            print("You have ", character_var.get_equipped_gun().get_ammo(), " shots remaining", sep='')
                        if "Goblin" in enemy_var.get_name() or enemy_var.get_equipped_armour() is None:
                            defend = 1
                        else:
                            defend = enemy_var.get_equipped_armour().get_item_value()
                        total_attack = (math.floor(hit / defend))
                        if enemy_var.get_equipped_armour() is not None:
                            enemy_var.get_equipped_armour().set_item_value((enemy_var.get_equipped_armour().
                                                                            get_item_value() - total_attack))
                        enemy_var.set_health(enemy_var.get_health() - total_attack)
                        if enemy_var.get_health() > 0:
                            enemy_attack(character_var, enemy_var, "yes")
                        else:
                            enemy_defeat(character_var, enemy_var)
                            loot_add(character_var, enemy_var)
                            break
                    else:
                        character_var.get_equipped_gun().set_ammo(character_var.get_equipped_gun().get_ammo() - 1)
                        print("You have ", character_var.get_equipped_gun().get_ammo(), " shots remaining", sep='')
                        enemy_attack(character_var, enemy_var, "no")
                else:
                    print("You are out of ammo.")
            else:
                print("You do not have a gun equipped.\nCheck your Inventory for any available guns to equip.")

        # TODO: update the flee option
        elif option == "4":
            if random.randint(0, 6) + character_var.get_luck_attribute() > 12:
                print("You escape battle with the ", enemy_var.name, ".", sep='')
                break
            else:
                new_hp = enemy_var.get_health() - character_var.get_strength_attribute()
                character_var.set_health_points(new_hp)
                print("You were unable to escape battle. \nHowever the ", enemy_var.name,
                      " was able to strike you.", sep='')
                if character_var.get_health_points() > 0:
                    print("Your health is now ", character_var.get_health_points(), ".", sep='')
                else:
                    game_over(character_var)
        elif option == "3":
            inventory(character_var)
            enemy_attack(character_var, enemy_var, "no")
        else:
            print("Option not allowed please choose either 1, 2 or 3.")
    print("Your current Score is ", character_var.get_exp(), sep='')



