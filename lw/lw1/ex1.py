# Exercise 1
# Given two numbers: a = 123, b = 543, compute:
# 1. The binary form of a
# 2. aXORb in binary form and in decimal form

a = 123
b = 543

a_bin = bin(123)[2:]
b_bin = bin(543)[2:]

print(f'1. The binary form of a: {a_bin}')
print(f"2. aXORb in binary form is '{bin(a^b)[2:]}' and in decimal form is '{int(bin(a^b)[2:], 2)}'")

# print(a_bin, b_bin, bin(a^b)[2:])

# a_bin = [int(bit) for bit in a_bin]
# b_bin = [int(bit) for bit in b_bin]


# result = ''
# while len(a_bin) != 0 and len(b_bin) != 0:
#   result += str(a_bin[-1]^b_bin[-1])
#   a_bin.pop()
#   b_bin.pop()

# while len(a_bin) != 0:
#   result += str(a_bin[-1]^0)
#   a_bin.pop()

# while len(b_bin) != 0:
#   result += str(b_bin[-1]^0)
#   b_bin.pop()

# print(result[::-1])