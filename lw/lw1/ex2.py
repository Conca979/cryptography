# Exercise 2
# Given a set of numbers
# A = {105, 110, 116, 114, 111, 50, 99, 114, 121, 112, 116, 111, 123, 119, 51, 108, 99, 48, 109, 51, 95, 116, 48, 95, 106, 48, 117, 114, 110, 51, 121, 125}
# find the message hidden behind it. Knowing that each number in the set is the ascii code
# of a letter in the hidden message.

A = [105, 110, 116, 114, 111, 50, 99, 114, 121, 112, 116, 111, 123, 119, 51, 108, 99, 48, 109, 51, 95, 116, 48, 95, 106, 48, 117, 114, 110, 51, 121, 125]

result = ''

for c in A:
  result += chr(c)

print(str(result))