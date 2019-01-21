def process_caesar_shift(message, shift_amount):
    try:
        s = int(shift_amount)  # Used 15 in provided output
    except:
        s = 0

    n = lambda letter: 65 if letter.isupper() else 97

    return ''.join([chr((ord(a) + s - n(a)) % 26 + n(a)) if a.isalpha() else a for a in message])
