#!/usr/bin/env python

import csv
csv.field_size_limit( 1310720 )

def get_column_from_csv_path( column_name, csv_path ):
    result = [
        line[ column_name ] if column_name in line else None
        for line in csv.DictReader( open( csv_path ) )
        ]
    
    if None in result:
        ## If the column name isn't in one row, it shouldn't be in any rows.
        assert all([ e is None for e in result ])
        raise KeyError( 'Column name does not exist: ' + column_name )
    
    return result

def get_lines_matching_column_values_from_csv_path( column_name2values, csv_path ):
    return [
        line for line in csv.DictReader( open( csv_path ) )
        if all([
            line[name] == value
            for name, value in column_name2values.iteritems()
            ])
        ]

def main():
    import os, sys
    
    def usage():
        print >> sys.stderr, 'Usage:', sys.argv[0], 'path/to/file.csv column_name'
        sys.exit(-1)
    
    try:
        csv_path, column_name = sys.argv[1:]
    except:
        usage()
    
    if not os.path.exists( csv_path ):
        usage()
    
    
    column = get_column_from_csv_path( column_name, csv_path )
    
    ## Transpose the column into a row:
    # print ','.join( column )
    
    for el in column: print el

if __name__ == '__main__': main()
