class Enemy:
    def __init__(self, health, defence, strength, gun_skill, luck):
        self.name = ''
        self.hp = health
        self.dp = defence
        self.inventory = []
        self.strength_attribute = strength
        self.gun_skill_attribute = gun_skill
        self.luck_attribute = luck
        self.happy = 0
