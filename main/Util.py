import textwrap

def vowel_start(word):
    vowel = 'aeiou'
    if word[0].lower() in vowel:
        start = "An "
    else:
        start = "A "
    return start

def use_textwrap(value):
    dedented_text = textwrap.dedent(value).strip()
    print(dedented_text)
