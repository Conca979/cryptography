# Find multiplicative inverse of x = 65537 in the modulo N = 35256.

from ex1 import gcd

# Extended Euclidean Algorithm
# We need to find a and b such that x*a + N*b = gcd(x, N) = 1

# a^b mod c = 1: base^mul_inv mod modulus = 1
a = 65537
c = 35256

def find_mod_inverse(base, modulus):
  # Initialization
  t_1 = 0
  t_2 = 1
  q = 0
  r = 0
  t = 0
  o_m = modulus

  while True:
    r = modulus % base
    if r == 0: break

    q = modulus // base
    t = t_1 - q * t_2

    t_1 = t_2
    t_2 = t

    modulus = base
    base = r

  return t_2 if t_2 >= 0 else t_2 + o_m

if __name__ == "__main__":
  if gcd(a, c) != 1:
    print(f"{a} and {c} are not coprime)")
    exit(0)
  
  b = find_mod_inverse(a, c)

  if (a*b) % c:
    print(f"result is {b}")