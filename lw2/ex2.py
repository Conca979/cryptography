# Given a set of numbers
# A = {290345, 218585, 143231, 164172, 155768, 423151, 239707, 153544, 287390, 480837}
# find all pairs of number that are relatively prime to each other.

from ex1 import gcd

A = [290345, 218585, 143231, 164172, 155768, 423151, 239707, 153544, 287390, 480837]

result = []

for id_1 in range(len(A)):
  if id_1 == len(A) - 1: break
  for id_2 in range(id_1 + 1, len(A)):
    if gcd(A[id_1], A[id_2]) == 1:
      result.append((A[id_1], A[id_2]))

print(result, len(result))