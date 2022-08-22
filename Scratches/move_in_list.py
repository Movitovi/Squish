l = [0,1,2,3,4,5]

old_i = 2
new_i = 0

def move_item(list, old_i, new_i):
    list.insert(new_i, list.pop(old_i))
    return list

print(move_item(l, old_i, new_i))