
def dialog_system(hero, responses):
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