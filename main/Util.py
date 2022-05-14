
def vowel_start(word):
    vowel = 'aeiou'
    if word[0].lower() in vowel:
        start = "An "
    else:
        start = "A "
    return start