# Given two numbers: a = 52698, b = 61430, compute great common divisor of a and b.

a = 52698
b = 61430

# Extended Euclidean Algorithm
def gcd(num_1, num_2):
  if num_1 < num_2:
    num_1, num_2 = num_2, num_1

  if num_2 == 0:
    return num_1

  return gcd(num_2, num_1 % num_2)

if __name__ == '__main__':
  print(gcd(a, b)) # 2