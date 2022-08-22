import os

def shift_chars(input_string, shift_amount):
    s = input_string.encode('utf-16').hex()
    total_shift = 0
    for i in range(0, len(s)):
        total_shift += shift_amount * (16 ** i)
    return bytes.fromhex(hex((int(s, 16) + total_shift) % (16 ** len(s)))[2:]).decode('utf-16')[1:]

cwd = os.getcwd()
file = open(os.path.join(cwd, 'secrets_decoded.txt'), encoding = 'utf-16')
secrets = file.read()
file.close()
s = shift_chars(secrets, 1)#.split('\n')

file = open(os.path.join(cwd, 'secrets.txt'), mode = 'w', encoding = 'utf-16')
file.write(s)
file.close()

print(s)