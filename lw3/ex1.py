# Given a message ”flow” (in ascii code), find the corresponding integer number representing this message in Python.
# Hint: how to convert a string to int in python?

# let q, p large primes

msg = 'flow'[::-1]

result = 0
for i in range(len(msg)):
  result += ord(msg[i])*(256**i)

print(result)