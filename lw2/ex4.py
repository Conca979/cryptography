# Find multiplicative inverse of x = 65537 in the modulo N = 35256.

x = 65537
N = 35256

from ex1 import gcd

# Extended Euclidean Algorithm
# We need to find a and b such that x*a + N*b = gcd(x, N) = 1


if __name__ == "__main__":
  print(f"{x} and {N} are {'not ' if gcd(65537, 35256) != 1 else ''}coprime")