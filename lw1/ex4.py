# Based on the provided description of the A5/1 cipher, implement the A5/1 Key generation algorithm. List n the keystream bits, suppose that the values of registers are provided
# X0, Y0, Z0
# Test the program with following register values in decimal:
# X = (x0, x1, ..., x18) = (513365)10
# Y = (y0, y1, ..., y21) = (3355443)10
# Z = (z0, z1, ..., z22) = (7401712)10
# n = 10

# -------------------------------------------------

def _new_bits(params, bits):
    x_r = bits[params[0]]
    for i in params[1:]:
        x_r = x_r ^ bits[i]
    return x_r

def _majority(d, m_i):
    s = 0
    for k in d:
        s += d[k][0][m_i[k]]
    return 0 if s <= 1 else 1

def _new_s0(b):
    return b[0][0][-1]^b[1][0][-1]^b[2][0][-1]

def bit_generator(length, d, m_i):
    result = ''
    for _ in range(length):
        m = _majority(d=d, m_i=m_i)

        s = _new_s0(list(d.values()))
        result += str(s)

        for k in d:
            if d[k][0][m_i[k]] == m:
                k_0 = _new_bits(bits=d[k][0], params=d[k][1])
                d[k][0].pop()
                d[k][0] = [k_0] + d[k][0]

    return result
        

#------------------------------------------------------------

x = bin(513365)[2:]
y = bin(3355443)[2:]
z = bin(7401712)[2:]

x = [int(i) for i in x]
y = [int(i) for i in y]
z = [int(i) for i in z]

# print(len(x), len(y), len(z), '=', len(x+y+z) == 64)

x_id = [13, 16, 17, 18]
y_id = [20, 21]
z_id = [20, 21, 22]

print(bit_generator(length=10,
                    d={'x': [x, x_id],
                       'y': [y, y_id],
                       'z': [z, z_id]},
                    m_i= {'x': 8,
                          'y': 10,
                          'z': 10}))