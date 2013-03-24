#!/opt/local/bin/python

def pretty_print_ascii( questions, important = frozenset(), feedback = '', author = '' ):
    
    imp = frozenset( important )
    
    print 'Author:', author
    
    for i, q_and_a in enumerate( questions['questions'] ):
        print '%s %d. %s %s' % ( ('*' if i in imp else ' '), i, q_and_a['q'], q_and_a['a'] )
    
    print '  I reached the end.'
    print 'Feedback:', feedback

def test():
    qs = [{'q': 'Is it science fiction', 'a': True}, {'q': 'Does it involve 3-legged aliens with luminous heads?', 'a': True}, {'q': 'Do they abduct sheep from a remote Scottish island?', 'a': True}, {'q': 'Do the sheep escape?', 'a': True}, {'q': 'Do they escape by fashioning a makeshift glider from bits of metal?', 'a': False}, {'q': 'Do they fashion a glider of any sort? Does the escape involve a glider?', 'a': True}, {'q': 'Do they shear themselves and knit the glider from wool?', 'a': False}]
    
    imp = [0, 2, 3, 5]
    
    pretty_print( qs, imp )

def main():
    #test()
    
    import sys
    
    def usage():
        print >> sys.stderr, 'Usage:', sys.argv[0], 'path/to/results1.csv [path/to/results2.csv ... path/to/resultsN.csv]'
        sys.exit(-1)
    
    if len( sys.argv ) == 1: usage()
    
    import csv, json
    csv.field_size_limit( 1310720 )
    
    from WorkerId2RandomId.WorkerId2RandomId import WorkerId2RandomId
    
    for path in sys.argv[1:]:
        for line in csv.DictReader( open( path ) ):
            pretty_print_ascii(
                json.loads( json.loads( line['payload'] )[0] ),
                json.loads( json.loads( line['influential_questions'] )[0] ),
                json.loads( line['feedback'] )[0],
                WorkerId2RandomId[ line['WorkerId'] ]
                )
            print '--------------------------'

if __name__ == '__main__': main()
