
class Dialog:
    def __init__(self,used, sum, text):
        self.used = used
        self.sum = sum
        self.text = text


    def get_dialog_used(self):
        return self.used

    def set_dialog_used(self, used):
        self.used = used

    def get_dialog_sum(self):
        return self.sum

    def set_dialog_sum(self, sum):
        self.sum = sum

    def get_dialog_text(self):
        return self.text

    def set_dialog_text(self, text):
        self.text = text



class HeroDialog(Dialog):
    def __init__(self,used, sum, text, agro):
        super().__init__(used, sum,text)
        self.agro = agro

    def get_dialog_agro(self):
        return self.agro

    def set_dialog_agro(self, agro):
        self.agro = agro

class ResponseDialog(Dialog):
    def __init__(self,used, sum, text, value):
        super().__init__(used,sum,text)
        self.value = value

    def get_dialog_value(self):
        return self.value

    def set_dialog_value(self, value):
        self.value = value