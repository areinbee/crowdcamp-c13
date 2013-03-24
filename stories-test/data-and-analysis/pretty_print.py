qs = [{'q': 'Is it science fiction', 'a': True}, {'q': 'Does it involve 3-legged aliens with luminous heads?', 'a': True}, {'q': 'Do they abduct sheep from a remote Scottish island?', 'a': True}, {'q': 'Do the sheep escape?', 'a': True}, {'q': 'Do they escape by fashioning a makeshift glider from bits of metal?', 'a': False}, {'q': 'Do they fashion a glider of any sort? Does the escape involve a glider?', 'a': True}, {'q': 'Do they shear themselves and knit the glider from wool?', 'a': False}]

imp = [0, 2, 3, 5]

for i, q in enumerate( qs ):
    print '%s %d. %s %s' % ( ('*' if i in imp else ' '), i, q['q'], q['a'] )

print '  I reached the end.'