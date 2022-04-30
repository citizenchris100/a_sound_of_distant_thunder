import random
import math
from operator import attrgetter
from itertools import groupby


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
    if random.randint(0, 6) < enemy_var.get_luck():
        if "Goblin" in enemy_var.get_name() or enemy_var.get_equipped_gun() is None:
            if hit_enemy == "yes":
                print("They were able to strike back with a melee attack")
            else:
                print("They hit you with a melee attack")
            if "Goblin" in enemy_var.get_name() or enemy_var.get_equipped_melee() is None:
                hit = enemy_var.get_strength()
            else:
                hit = (enemy_var.get_strength() + enemy_var.get_equipped_melee().get_item_value())
        else:
            if hit_enemy == "yes":
                print("They were able to strike back with their fire arm")
            else:
                print("They fire at you with their gun.")
            if random.randint(0, 12) < enemy_var.get_luck():
                hit = ((enemy_var.get_gun_skill() + enemy_var.get_equipped_gun().get_item_value()) * 2)
            else:
                hit = (enemy_var.get_gun_skill() + enemy_var.get_equipped_gun().get_item_value())
        if character_var.get_equipped_armour() is not None:
            defend = character_var.get_defence_points() + character_var.get_equipped_armour().get_item_value()
        else:
            defend = character_var.get_defence_points()
        character_var.set_health_points(math.floor(character_var.get_health_points() - (hit / defend)))
        if character_var.hp > 0:
            print("Your health is now ", character_var.get_health_points(), ".", sep='')
        else:
            game_over(character_var)
    else:
        print("They attempted to strike you, however you deflected the attack.")


def vowel_start(word):
    vowel = 'aeiou'
    if word[0].lower() in vowel:
        start = "An "
    else:
        start = "A "
    return start


# TODO: complete level up
def level_up(character_var):
    if 0 <= character_var.get_lvl() <= 1:
        if 25 <= character_var.get_exp():
            upgrade_character(character_var, 1, 5)
    elif 1 <= character_var.get_lvl() <= 2:
        if 50 <= character_var.get_exp():
            character_var.up_lvl()
    elif 2 <= character_var.get_lvl() <= 3:
        if 100 <= character_var.get_exp():
            character_var.up_lvl()
    elif 3 <= character_var.get_lvl() <= 4:
        if 175 <= character_var.get_exp():
            character_var.up_lvl()
    elif 4 <= character_var.get_lvl() <= 5:
        if 275 <= character_var.get_exp():
            character_var.up_lvl()
    elif 5 <= character_var.get_lvl() <= 6:
        if 475 <= character_var.get_exp():
            character_var.up_lvl()
    elif 6 <= character_var.get_lvl() <= 7:
        if 775 <= character_var.get_exp():
            character_var.up_lvl()
    elif 7 <= character_var.get_lvl() <= 7:
        if 1775 <= character_var.get_exp():
            character_var.up_lvl()


def upgrade_character(character_var, dp, hp):
    option = input("You have leveled up.\nChoose which attribute you would like to improve.\n"
                   "1. Melee Attack\n2. Gun Skill\n3. Luck\n4. Charm\nHelp\n> ")
    if option == "1":
        character_var.set_strength_attribute(character_var.get_strength_attribute() + 1)
    elif option == "2":
        character_var.set_gun_skill(character_var.get_gun_skill() + 1)
    elif option == "3":
        character_var.set_luck_attribute(character_var.get_luck_attribute() + 1)
    elif option == "4":
        character_var.set_charm_attribute(character_var.get_charm_attribute() + 1)
    elif option.lower() == "help":
        print('------------------------------')
        print('-About the Character         -')
        print('-Attributes                  -')
        print('------------------------------')
        print('------------------------------')
        print('-Melee Attack: affects how   -')
        print('-you use hand help weapons   -')
        print('-such as knives.             -')
        print('------------------------------')
        print('-Gun Skill: affects your     -')
        print('-ability to use hand guns    -')
        print('-and rifles.                 -')
        print('------------------------------')
        print('-Luck: can greatly affect    -')
        print('-the outcome of battles and  -')
        print('-your chance of getting loot.-')
        print('------------------------------')
        print('-Charm: affects how well     -')
        print('-you can persuade others     -')
        print('------------------------------')
        upgrade_character(character_var, dp, hp)
    else:
        print("Invalid Input, please select an Attribute you wish to upgrade. \nIf you need more information "
              "about the Class Attributes type \'Help\'")
        upgrade_character(character_var, dp, hp)
    character_var.up_lvl()
    character_var.set_hp_limit(character_var.get_hp_limit() + hp)
    character_var.set_health_points(character_var.get_health_points() + hp)
    character_var.set_defence_points(character_var.get_defence_points() + dp)
    print("Alex is now Level ", character_var.get_lvl(), "\nYou've gained ", hp,
          " health points & ", dp, " defence point", sep='')


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


def use_ammo(character_var):
    for i, item in enumerate(character_var.get_inventory()):
        if item.attribute == "ammo":
            character_var.get_inventory()[i].set_item_value((character_var.get_inventory()[i].get_item_value() - 1))


def battle_state(character_var, enemy_var, surprise):
    if surprise:
        enemy_attack(character_var, enemy_var, "surprise")
    while enemy_var.get_health() > 0:
        option = input("1. Melee Attack \n2. Gun Attack\n3. Inventory\n4. Flee\n> ")
        if option == "1":
            if random.randint(0, 6) < character_var.get_luck_attribute():
                if character_var.get_equipped_melee() is not None:
                    print("You swing your ", character_var.get_equipped_melee.get_item_name(), " attacking the ",
                          enemy_var.get_name(), ".", sep='')
                    hit = (character_var.get_strength_attribute() + character_var.get_equipped_melee.get_item_value())
                else:
                    print("You punch the ", enemy_var.get_name(), ".", sep='')
                    hit = character_var.get_strength_attribute()
                if enemy_var.get_equipped_armour() is not None:
                    defend = (enemy_var.get_defence() + enemy_var.get_equipped_armour.get_item_value())
                else:
                    defend = enemy_var.get_defence()
                enemy_var.set_health(math.floor(enemy_var.get_health - (hit / defend)))
                if enemy_var.get_health() > 0:
                    enemy_attack(character_var, enemy_var, "yes")
                else:
                    enemy_defeat(character_var, enemy_var)
                    if random.randint(0, 6) < character_var.get_luck_attribute():
                        loot_add(character_var, enemy_var)
                    break
            else:
                enemy_attack(character_var, enemy_var, "no")
        elif option == "2":
            if character_var.get_equipped_gun() is not None:
                if check_ammo(character_var)[0].get_item_value() > 0:
                    if random.randint(0, 6) < character_var.get_luck_attribute():
                        print("You fired your ", character_var.get_equipped_gun().get_item_name(), " attacking the ",
                              enemy_var.name, ".", sep='')
                        if random.randint(0, 12) < character_var.get_luck_attribute():
                            print("You managed to get two hits")
                            hit = ((character_var.get_equipped_gun().get_item_value() + character_var.get_gun_skill()) * 2)
                        else:
                            hit = (character_var.get_equipped_gun().get_item_value() + character_var.get_gun_skill())
                        if "Goblin" in enemy_var.get_name() or enemy_var.get_equipped_armour() is None:
                            defend = enemy_var.get_defence()
                        else:
                            defend = (enemy_var.get_defence() + enemy_var.get_equipped_armour().get_item_value())
                        enemy_var.set_health(enemy_var.get_health() - math.floor(hit / defend))
                        if enemy_var.get_health() > 0:
                            enemy_attack(character_var, enemy_var, "yes")
                        else:
                            enemy_defeat(character_var, enemy_var)
                            if random.randint(0, 6) < character_var.get_luck_attribute():
                                loot_add(character_var, enemy_var)
                            break
                    else:
                        enemy_attack(character_var, enemy_var, "no")
            else:
                print("You do not have a gun equipped.\nCheck your Inventory for any available guns to equip.")

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
        else:
            print("Option not allowed please choose either 1, 2 or 3.")
    print("Your current Score is ", character_var.get_exp(), sep='')


# TODO: system to add ammo to box
# TODO: add catch for empty inventory
# TODO: move to its own file
def inventory(character_var):
    print('------------------------------')
    print('-         Inventory          -')
    print('------------------------------')
    print('------------------------------')
    for i in range(len(character_var.get_inventory())):
        num = i + 1
        print(num, ": ", character_var.get_inventory()[i].get_item_name(), sep='')
    print('------------------------------')
    print('------------------------------')
    while True:
        n = input("Enter the number of the corresponding Inventory item\nyou would like to Use / Equip or Discard.\n"
                  "Additionally you can type \'Exit\' to return to the previous Menu.\n> ")
        if n.isdigit() and int(n) <= len(character_var.get_inventory()):
            nn = int(n) - 1
            start = vowel_start(character_var.get_inventory()[nn].get_item_name())
            if character_var.get_inventory()[nn].get_item_attribute() == "hp":
                print('------------------------------')
                print("Would you like to Use this ", character_var.get_inventory()[nn].get_item_name(), "?", sep='')
                print('------------------------------')
                d = input("1. Use.\n2. Discard.\n> ")
                if d.lower() == "use" or d == "1":
                    character_var.set_health_points((character_var.get_health_points() +
                                                     character_var.get_inventory()[nn].get_item_value()))
                    print('------------------------------')
                    print("You used ", start, character_var.get_inventory()[nn].get_item_name(), sep='')
                    print(character_var.get_inventory()[nn].get_item_value(), " was added to your Health.", sep='')
                    print("Your Health is now ", character_var.get_health_points(), sep='')
                    print('------------------------------')
                    character_var.del_inventory(nn)
                    break
                elif d.lower() == "discard" or d == "2":
                    print('------------------------------')
                    print("The ", character_var.get_inventory()[nn].get_item_name(), " will be deleted.", sep='')
                    print('------------------------------')
                    character_var.del_inventory(nn)
                    break
            elif character_var.get_inventory()[nn].get_item_attribute() == "gun" or \
                    character_var.get_inventory()[nn].get_item_attribute() == "melee" or \
                    character_var.get_inventory()[nn].get_item_attribute() == "armour":
                print('------------------------------')
                print("Would you like to eqip this ", character_var.get_inventory()[nn].get_item_name(), "?", sep='')
                print('------------------------------')
                d = input("1. Equip.\n2. Discard.\n> ")
                if d.lower() == "equip" or d == "1":
                    if character_var.get_inventory()[nn].get_item_attribute() == "gun":
                        if character_var.get_equipped_gun() is not None:
                            character_var.add_inventory(character_var.get_equipped_gun())
                        character_var.set_equipped_gun(character_var.get_inventory()[nn])
                        print('------------------------------')
                        print("The ", character_var.get_equipped_gun().get_item_name(), " is now equipped.", sep='')
                        print('------------------------------')
                    elif character_var.get_inventory()[nn].get_item_attribute() == "melee":
                        if character_var.get_equipped_melee() is not None:
                            character_var.add_inventory(character_var.get_equipped_melee())
                        character_var.set_equipped_melee(character_var.get_inventory()[nn])
                        print('------------------------------')
                        print("The ", character_var.get_equipped_melee().get_item_name(), " is now equipped.", sep='')
                        print('------------------------------')
                    elif character_var.get_inventory()[nn].get_item_attribute() == "armour":
                        if character_var.get_equipped_armour() is not None:
                            character_var.add_inventory(character_var.get_equipped_armour())
                        character_var.set_equipped_armour(character_var.get_inventory()[nn])
                        print('------------------------------')
                        print("The ", character_var.get_equipped_armour().get_item_name(), " is now equipped.", sep='')
                        print('------------------------------')
                    character_var.del_inventory(nn)
                    break
                elif d.lower() == "discard" or d == "2":
                    print("The ", character_var.get_equipped_armour().get_item_name(), " will be deleted.", sep='')
                    print('------------------------------')
                    character_var.del_inventory(nn)
                    break
                else:
                    print('Invalid Option. Please choose to either Equip or Discard the item.\n> ')
                    inventory(character_var)
        elif n.lower() == "exit":
            break
        else:
            print('Invalid Option. Please Enter the number of the corresponding '
                  'Inventory item you would like to use.\n> ')
            inventory(character_var)


def loot_add(character_var, enemy_var):
    loot_drop = enemy_var.get_inventory()[0]
    print("It appears to have dropped a ", loot_drop.get_item_name(), ".", sep='')
    print("Would you like to add ", loot_drop.get_item_name(), " to your Inventory?", sep='')
    option = input("Yes \nNo\n> ")
    if option.lower() == "yes":
        character_var.add_inventory(loot_drop)
        print(loot_drop.get_item_name(), " was added to your inventory.", sep='')
    elif option.lower() == "no":
        print("The ", loot_drop.get_item_name(), " is left behind.", sep='')
    else:
        print("Invalid Input, please choose either \'Yes\' or \'No\'.")
        loot_add(character_var, enemy_var)
