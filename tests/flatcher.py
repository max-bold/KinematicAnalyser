from FletcherChecksumLib import FletcherChecksumBytes, FletcherChecksumStr

bs = b'N4 M114'
# s = 'N4 M114'
# cs = FletcherChecksumBytes.get_fletcher16(bs)
# print(cs)
# print(cs['Fletcher16_dec'].to_bytes(2))
# cs = FletcherChecksumStr.get_fletcher16(s)
# print(cs)

# print(len(bs))
# sum1 = 0
# sum2 = 0
# for b in (bs):
#     sum1 = (sum1+b) % 255
#     # if sum1 >= 255:
#     #     sum1 -= 255
#     sum2 = (sum1+sum2) % 255
#     # if sum2 >= 255:
#     #     sum2 -= 255
# print(sum1, sum2)

# for b in b'35':
#     print(b)

# for b in bs:
#     print(b)
# l = len(bs)
# i = 0
# s1 = 0
# s2 = 0
# while l:
#     tl = l
#     if tl > 21:
#         tl = 21
#     l -= tl
#     while tl:
#         print(i, l, tl)

#         s1 = (s1 + bs[i]) % 255
#         i += 1
#         s2 = (s2+s1) % 255
#         tl -= 1
# print(s1, s2)
s = 0
for b in bs:
    s ^= b
print(s)

