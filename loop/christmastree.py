#!/usr/bin/env python2.7 -u

import time

'''
def wait_for_stories( HITId ):
    while True:
        stories = get_stories( HITId )
        print 'Got', len( stories ), 'stories.
        if len( stories ) == num_initial:
            return stories
        else:
            print 'Sleeping...'
            sleep( 60 )

def generate_stories( num_initial, num_iterations, num_to_keep ):
    
    for iteration in xrange( num_iterations ):
        if iteration == 0:
            HITId = create_HIT_for_generating_N_initial_stories( num_initial )
        else:
            truncated_stories = truncate_and_flip_stories_for_iteration_N_of_M( iteration, num_iterations )
            HITId = create_HIT_for_continuing_stories( truncated_stories )
        
        stories = wait_for_stories( HITId )
        
        db.record_stories_at_iteration( stories, iteration )
        
        stories_HTML = save_stories_to_HTML( stories )
        
        HITIds = publish_evaluations( stories_HTML, eval_questions, HIT_spec )
        evaluations = [ wait_for_evaluations( HITId ) for HITId in HITIds ]
        
        db.record_evaluations_at_iteration( evaluations, iteration )
        
        best_stories = keep_N_best_stories( stories, evaluations )
'''

kStateFilename = 'state.json'
kSleepSeconds = 60

def create_and_save_initial_state( params, out_dir ):
    ## If the version ever changes, we need to handle forward compatibility,
    ## perhaps in load_state_from_path().
    assert '1' == params['version']
    
    state_path = os.path.join( out_dir, kStateFilename )
    
    import json, copy
    state = copy.deepcopy( params )
    '''
    state['iterations'] is a list of dictionaries containing the
    information for the iteration.
    Each iteration dictionary has a 'stories' sequence,
    a 'stories_HITId' containing the HITId used to generate 'stories',
    a 'stories_count' specifying the number of desired 'stories',
    an 'evaluations' sequence,
    an 'evaluations_HITIds',
    a 'best_stories',
    and a 'continuing_stories'.
    '''
    state['iterations'] = []
    state['PC'] = 'generate_stories'
    
    save_state_to_path( state, state_path )
    print '[Saved initial state to "%s".]' % ( state_path, )
    
    return state

def save_state_to_path( state, state_path ):
    json.dump( state, open( state_path, 'w' ) )

def load_state_from_path( state_path ):
    state = json.load( open( state_path ) )
    
    ## If the version ever changes, we need to handle forward compatibility here.
    assert '1' == state['version']
    
    return state

def continue_from_state_path( state_path ):
    assert os.path.exists( state_path )
    
    state = load_state_from_path( state_path )
    
    while state['PC'] is not None:
        step_state( state )
        
        save_state_to_path( state, state_path )
        print '[Saved state to "%s".]' % ( state_path, )
    
    print 'Terminating.'

def step_state( state ):
    
    def generate_initial_stories_for_iteration
    
    if state['PC'] == 'prepare_to_generate_stories':
        if len( state['iterations'] ) == 0:
            state['PC'] = 'generate_initial_stories'
            return
        else:
            
            iter = state['iterations'][-1]
            
            truncated_stories = truncate_and_flip_stories_for_iteration_N_of_M( iter['stories'], len( state['iterations'] ), state['max_iterations'] )
            state['iterations'].append( {
                'continuing_stories': truncated_stories
                } )
            
            state['PC'] = 'generate_continuing_stories'
            return
    
    elif state['PC'] == 'generate_continuing_stories':
        ### 1 Create the HIT for generating the stories.
        ### 2 Move into 'wait_for_stories' state.
        assert len( state['iterations'] ) > 0
        assert 'continuing_stories' in state['iterations'][-1]
        
        iter = state['iterations'][-1]
        HITIds = create_HITs_for_continuing_stories( iter['continuing_stories'] )
        
        state['iterations'].append( {
            'stories_HITIds': create_HIT_for_generating_N_initial_stories( state['num_initial'] ),
            'stories_count': state['num_initial']
            } )
        state['PC'] = 'wait_for_stories'
        return
    
    elif state['PC'] == 'generate_initial_stories':
        ### 1 Create the HIT for generating the stories.
        ### 2 Move into 'wait_for_stories' state.
        assert len( state['iterations'] ) == 0
        state['iterations'].append( {
            'stories_HITIds': [ create_HIT_for_generating_N_initial_stories( state['num_initial'] ) ],
            'stories_count': state['num_initial']
            } )
        state['PC'] = 'wait_for_stories'
        return
    
    elif state['PC'] == 'wait_for_stories':
        ### 1 Check if all stories are in.
        ### 2 If not, sleep.
        ### 3 If so, move into create_evaluation() state.
        assert len( state['iterations'] ) > 0
        assert 'stories_HITId' in state['iterations'][-1]
        
        iter = state['iterations'][-1]
        HITId = iter['stories_HITId']
        
        stories = get_stories( HITId )
        iter['stories'] = stories
        
        print 'Got %d/%d stories.' % ( len( stories ), iter['stories_count'] )
        if len( stories ) == iter['stories_count']:
            state['PC'] = 'evaluate_stories'
            return
        else:
            print 'Sleeping...'
            time.sleep( kSleepSeconds )
            return
        
        missing = False
        for i, HITId in enumerate( HITIds ):
            if len( iter['stories'][i] ) < iter['stories_count']:
                evaluations = get_evaluations( HITId )
                iter['evaluations'][i] = evaluations
            
            print 'Got %d/%d evaluations.' % ( len( evaluations ), state['evaluation_params']['num_evaluations_per_story'] )
            
            if len( iter['evaluations'][i] ) < state['evaluation_params']['num_evaluations_per_story']:
                missing = True
        
        if missing:
            print 'Sleeping...'
            time.sleep( kSleepSeconds )
            return
        else:
            state['PC'] = 'keep_best_stories'
            return
    
    elif state['PC'] == 'evaluate_stories':
        ### 1 Create the HIT for evaluating the stories.
        ### 2 Move into 'wait_for_evaluations' state.
        assert len( state['iterations'] ) > 0
        assert len( state['iterations'][-1]['stories'] ) == state['iterations'][-1]['stories_count']
        
        iter = state['iterations'][-1]
        
        HITIds = publish_evaluations( iter['stories'], state['evaluation_params'] )
        iter['evaluations_HITIds'] = HITIds
        
        state['PC'] = 'wait_for_evaluations'
        return
    
    elif state['PC'] == 'wait_for_evaluations':
        ### 1 Check if all evaluations are in.
        ### 2 If not, sleep.
        ### 3 If so, move into create_evaluation() state.
        assert len( state['iterations'] ) > 0
        assert 'stories_HITId' in state['iterations'][-1]
        
        iter = state['iterations'][-1]
        HITIds = iter['evaluation_HITIds']
        
        missing = False
        for i, HITId in enumerate( HITIds ):
            if len( iter['evaluations'][i] ) < state['evaluation_params']['num_evaluations_per_story']:
                evaluations = get_evaluations( HITId )
                iter['evaluations'][i] = evaluations
            
            print 'Got %d/%d evaluations.' % ( len( evaluations ), state['evaluation_params']['num_evaluations_per_story'] )
            
            if len( iter['evaluations'][i] ) < state['evaluation_params']['num_evaluations_per_story']:
                missing = True
        
        if missing:
            print 'Sleeping...'
            time.sleep( kSleepSeconds )
            return
        else:
            state['PC'] = 'keep_best_stories'
            return
    
    elif state['PC'] == 'keep_best_stories':
        ### 1 Create the HIT for evaluating the stories.
        ### 2 Move into 'wait_for_evaluations' state.
        assert len( state['iterations'] ) > 0
        assert len( state['iterations'][-1]['evaluations'] ) == state['evaluation_params']['num_evaluations_per_story']
        
        iter = state['iterations'][-1]
        
        best_stories = keep_N_best_stories( iter['stories'], iter['evaluations'], state['keep_N_best_stories'] )
        iter['continuing_stories'] = best_stories
        
        if len( state['iterations'] ) == state['max_iterations']:
            state['PC'] = None
            return
        else:
            state['PC'] = 'prepare_to_generate_stories'
            return
    
    elif state['PC'] == 'prepare_to_generate_stories':
        
    
        HITIds = publish_evaluations( iter['stories'], state['evaluation_params'] )
        iter['evaluations_HITIds'] = HITIds
        
        state['PC'] = 'wait_for_evaluations'
        return
    
    def generate_stories( num_initial, num_iterations, num_to_keep ):
    
    for iteration in xrange( num_iterations ):
        if iteration == 0:
            HITId = create_HIT_for_generating_N_initial_stories( num_initial )
        else:
            truncated_stories = truncate_and_flip_stories_for_iteration_N_of_M( iteration, num_iterations )
            HITId = create_HIT_for_continuing_stories( truncated_stories )
        
        stories = wait_for_stories( HITId )
        
        db.record_stories_at_iteration( stories, iteration )
        
        stories_HTML = save_stories_to_HTML( stories )
        
        HITIds = publish_evaluations( stories_HTML, eval_questions, HIT_spec )
        evaluations = [ wait_for_evaluations( HITId ) for HITId in HITIds ]
        
        db.record_evaluations_at_iteration( evaluations, iteration )
        
        best_stories = keep_N_best_stories( stories, evaluations )

def main():
    import sys, os
    
    def usage():
        print >> sys.stderr, 'Usage:', sys.argv[0], 'path/to/params.json path/to/output/'
        #print >> sys.stderr, 'Example:', sys.argv[0], 'data/computer-strokes-ah/example.json data/computer-strokes-ah/exampleN | tee -a data/computer-strokes-ah/exampleN-stdout.txt'
        sys.exit(-1)
    
    argv = list( sys.argv )
    del argv[0]
    
    if len( argv ) not in ( 2, ): usage()
    
    params_path = argv[0]
    del argv[0]
    
    out_path = argv[0]
    del argv[0]
    
    ## Make the output path if it doesn't exist.
    if not os.path.exists( out_path ): os.makedirs( out_path )
    if not os.path.isdir( out_path ): usage()
    
    print 'Running:', ' '.join( sys.argv )
    
    state_path = os.path.join( out_path, kStateFilename )
    
    if not os.path.exists( state_path ):
        ## Now load in the rest of the parameters.
        import json
        params = json.load( open( params_path ) )
        
        create_and_save_initial_state( params, state_path )
    
    assert os.path.exists( state_path )
    
    result = continue_from_state_path_v1( state_path = state_path )

if __name__ == '__main__': main()
