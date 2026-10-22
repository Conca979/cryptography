# Given a set of numbers
# B = {99, 100, 126, 120, 101, 56, 105, 120, 115, 122, 126, 101, 113, 59, 121, 126, 57, 122, 85, 58, 100, 85, 96, 58, 127, 120, 100, 57, 115, 119}
# find the message hidden behind it. Clues are as below:
# 1. each number in the set is a xor of a hidden number and the number k = 10 (decimal)
# 2. each hidden number is an ascii code of a letter in the message.

B = [99, 100, 126, 120, 101, 56, 105, 120, 115, 122, 126, 101, 113, 59, 121, 126, 57, 122, 85, 58, 100, 85, 96, 58, 127, 120, 100, 57, 115, 119]

result = ''
K = 10

for bit in B:
  result += chr(bit^K)

print(result)