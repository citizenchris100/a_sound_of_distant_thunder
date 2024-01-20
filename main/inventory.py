from Util import vowel_start


def inventory(character_var):
    print('------------------------------')
    print('-         Inventory          -')
    print('------------------------------')
    print('------------------------------')
    if len(character_var.get_inventory()) < 1:
        print('-           Empty            -')
        print('------------------------------')
        print('------------------------------')
    else:
        while True:
            print('------------------------------')
            print('------------------------------')
            for i in range(len(character_var.get_inventory())):
                num = i + 1
                print(num, ": ", character_var.get_inventory()[i].get_item_name(), sep='')
            print('------------------------------')
            print('------------------------------')
            n = input(
                "Enter the number of the corresponding Inventory item\nyou would like to Use / Equip or Discard.\n"
                "Additionally you can type \'Exit\' to return to the previous Menu.\n> ")
            if n.isdigit() and int(n) <= len(character_var.get_inventory()):
                nn = int(n) - 1
                start = vowel_start(character_var.get_inventory()[nn].get_item_name())
                # TODO add gibberish option catches for every category
                if character_var.get_inventory()[nn].get_item_attribute() == "hp":
                    print('------------------------------')
                    print("Would you like to Use this ", character_var.get_inventory()[nn].get_item_name(), "?", sep='')
                    print('------------------------------')
                    d = input("1. Use.\n2. Discard.\n> ")
                    if d.lower() == "use" or d == "1":
                        if character_var.get_health_points() < character_var.get_hp_limit():
                            character_var.set_health_points((character_var.get_health_points() +
                                                         character_var.get_inventory()[nn].get_item_value()))
                            print('------------------------------')
                            print("You used ", start, character_var.get_inventory()[nn].get_item_name(), sep='')
                            print(character_var.get_inventory()[nn].get_item_value(), " was added to your Health.", sep='')
                            print("Your Health is now ", character_var.get_health_points(), sep='')
                            print('------------------------------')
                            character_var.del_inventory(nn)
                            break
                        else:
                            print('------------------------------')
                            print('------------------------------')
                            print("Your Health is already Max")

                    elif d.lower() == "discard" or d == "2":
                        discard(character_var, nn)
                        break
                elif character_var.get_inventory()[nn].get_item_attribute() == "gun" or \
                        character_var.get_inventory()[nn].get_item_attribute() == "melee" or \
                        character_var.get_inventory()[nn].get_item_attribute() == "armour":
                    print('------------------------------')
                    print("Would you like to eqip this ", character_var.get_inventory()[nn].get_item_name(), "?",
                          sep='')
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
                            print("The ", character_var.get_equipped_melee().get_item_name(), " is now equipped.",
                                  sep='')
                            print('------------------------------')
                        elif character_var.get_inventory()[nn].get_item_attribute() == "armour":
                            if character_var.get_equipped_armour() is not None:
                                character_var.add_inventory(character_var.get_equipped_armour())
                            character_var.set_equipped_armour(character_var.get_inventory()[nn])
                            print('------------------------------')
                            print("The ", character_var.get_equipped_armour().get_item_name(), " is now equipped.",
                                  sep='')
                            print('------------------------------')
                        character_var.del_inventory(nn)
                        break
                    elif d.lower() == "discard" or d == "2":
                        discard(character_var, nn)
                        break
                    else:
                        print('Invalid Option. Please choose to either Equip or Discard the item.\n> ')
                elif character_var.get_inventory()[nn].get_item_attribute() == "ammo":
                    print('------------------------------')
                    print("There are ", character_var.get_inventory()[nn].get_item_value(),
                          " rounds remaining within this ", character_var.get_inventory()[nn].get_item_name(), ".",
                          sep='')
                    print('------------------------------')
                    if character_var.get_equipped_gun() is not None:
                        if character_var.get_equipped_gun().get_ammo() < character_var.get_equipped_gun().get_limit() \
                                and character_var.get_inventory()[nn].get_item_value() > 0:
                            print('------------------------------')
                            print("Would you like to reload ?")
                            print('------------------------------')
                            d = input("1. Yes.\n2. No.\n> ")
                            if "yes" in d.lower() or d == "1":
                                ammo_needed = character_var.get_equipped_gun().get_limit() - \
                                              character_var.get_equipped_gun().get_ammo()
                                if ammo_needed < character_var.get_inventory()[nn].get_item_value():
                                    character_var.get_equipped_gun().set_ammo(
                                        character_var.get_equipped_gun().get_ammo()
                                        + ammo_needed)
                                    character_var.get_inventory()[nn].set_item_value(character_var.get_inventory()[nn].
                                                                                     get_item_value() - ammo_needed)
                                    print("There are now", character_var.get_inventory()[nn].get_item_value(),
                                          " rounds remaining within this",
                                          character_var.get_inventory()[nn].get_item_name(),
                                          ".", sep='')
                                    print('------------------------------')
                                    break
                                else:
                                    character_var.get_equipped_gun().set_ammo(
                                        character_var.get_equipped_gun().get_ammo()
                                        + character_var.get_inventory()[nn].
                                        get_item_value())
                                    character_var.get_inventory()[nn].set_item_value(0)
                                    print("There are now ", character_var.get_inventory()[nn].get_item_value(),
                                          " rounds remaining within this",
                                          character_var.get_inventory()[nn].get_item_name(),
                                          ".", sep='')
                                    print("You were not able to fully reload your weapon.")
                                    print('------------------------------')
                                    break
                            if "no" in d.lower() or d == "2":
                                discard(character_var, nn)
                        else:
                            discard(character_var, nn)
                    else:
                        discard(character_var, nn)
            elif "exit" in n.lower():
                break
            else:
                print('Invalid Option. Please Enter the number of the corresponding '
                      'Inventory item you would like to use.\n> ')


def discard(character_var, nn):
    print('------------------------------')
    print("Would you like to discard this ",
          character_var.get_inventory()[nn].get_item_name(),
          "?", sep='')
    while True:
        print('------------------------------')
        e = input("1. Yes.\n2. No.\n> ")
        if "yes" in e.lower() or e == "1":
            character_var.del_inventory(nn)
        elif "no" in e.lower() or e == "2":
            break
        else:
            print("Invalid Option.")
            break


def loot_add(character_var, enemy_var):
    while True:
        print('------------------------------')
        print('------------------------------')
        print('-      Enemy Inventory       -')
        print('------------------------------')
        print('------------------------------')
        if len(enemy_var.get_inventory()) < 1:
            print('-           Empty            -')
            print('------------------------------')
            print('------------------------------')
            break
        else:
            for i in range(len(enemy_var.get_inventory())):
                num = i + 1
                print(num, ": ", enemy_var.get_inventory()[i].get_item_name(), sep='')
                print('------------------------------')
                print('------------------------------')
                n = input("Enter the number of the corresponding Inventory item\nyou would like to Add to your "
                          "current inventory.\n"
                          "Additionally you can type \'All\' to Add all of the items to your Inventory.\n"
                          "Enter \'Inventory\' to view your current inventory."
                          "\nYou can also enter\'Exit\' to return to the previous Menu.\n> ")
                if n.isdigit() and int(n) <= len(enemy_var.get_inventory()):
                    nn = int(n) - 1
                    character_var.add_inventory(enemy_var.get_inventory()[nn])
                    enemy_var.del_inventory(enemy_var.get_inventory()[nn])
                    if len(enemy_var.get_inventory()) < 1:
                        break
                elif "all" in n.lower():
                    if (len(character_var.get_inventory()) + len(enemy_var.get_inventory())) > character_var. \
                            get_inventory_limit():
                        print('------------------------------')
                        print("You do not have enough room in your Inventory for all of these Items.")
                    else:
                        for i in enemy_var.get_inventory():
                            character_var.get_inventory().append(i)
                            enemy_var.del_inventory(i)
                            break
                elif "exit" in n.lower():
                    break
                elif "inventory" in n.lower():
                    print("food")


