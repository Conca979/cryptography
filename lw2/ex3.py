# Based on the provided description of the square- and-multiply algorithm, calculate exponentiation:

# x^e mod m

# Compute:

# 856^25 mod 7

# Show the manual computation using the algorithm and compare it to returned results from your program.

# a^b mod c: base^exponential mod Modulus

a = 856
b = 25
c = 7

def mod_exp(base, exponential, modulus):
  a = bin(exponential)[3:]

  # Initialization
  original_base = base
  base = base % modulus
  for id in a:
    # print(id)
    if id == '0':
      base = base**2 % modulus
    else: # id == '1'
      base = ((base**2 % modulus) * original_base) % modulus

  return base
      



if __name__ == "__main__":
  print(mod_exp(base=a, exponential=b, modulus=c))