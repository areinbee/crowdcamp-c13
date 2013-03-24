#!/opt/local/bin/python

import os, csv
## In case we ever need it, here is how to increase the field size limit.
# csv.field_size_limit( 1310720 )

kCSVPath = 'WorkerId2RandomId.csv'
kCSVPath = os.path.join( os.path.dirname( os.path.realpath( os.path.abspath( __file__ ) ) ), kCSVPath )

WorkerId2RandomId = dict([ ( line['WorkerId'], line['RandomId'] ) for line in csv.DictReader( open( kCSVPath ) ) ])

def write():
    print 'Writing to CSV path:', kCSVPath
    with open( kCSVPath, 'wb' ) as csvfile:
        writer = csv.writer( csvfile )
        writer.writerow( ['WorkerId','RandomId'] )
        for w, r in WorkerId2RandomId.iteritems():
            writer.writerow( [ w, r ] )
    
    print 'Wrote %d IDs.' % ( len( WorkerId2RandomId ), )

def addWorkerIds( WorkerIds ):
    import uuid
    
    count = 0
    
    for WorkerId in WorkerIds:
        if WorkerId not in WorkerId2RandomId:
            WorkerId2RandomId[ WorkerId ] = uuid.uuid4()
            count += 1
    
    return count

def main():
    import sys
    
    def usage():
        print >> sys.stderr, 'Usage:', sys.argv[0], 'path/to/csv_file_with_a_column_named_WorkerId.csv [another another ...]'
        sys.exit(-1)
    
    if len( sys.argv ) == 1: usage()
    
    for path in sys.argv[1:]:
        added = addWorkerIds( [ line['WorkerId'] for line in csv.DictReader( open( path ) ) if 'WorkerId' in line ] )
        print 'Added %d unseen WorkerIds from: %s' % ( added, path )
    
    write()

if __name__ == '__main__': main()
