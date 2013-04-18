#!/usr/bin/env python2.7 -u

import time, json
import stories, evaluation

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
    
    import copy
    state['params'] = copy.deepcopy( params )
    state['version'] = state['params']['version']
    '''
    state['iterations'] is a list of dictionaries containing the
    information for the iteration.
    Each iteration dictionary looks as follows (use the 'db' module to get story or evaluation information from an assignment id):
    
    def create_fake_Nth_iteration():
    	return {
    		'stories': {
    			'HITIds': [ 'H1390', 'H192038' ],
    			'num_stories_per_HIT': 2,
    			
    			'parent_story_ids': [ 'S8', 'S9' ],
    			'result_story_ids': [ [ 'S10', 'S11' ], [ 'S12', 'S13' ] ]
    			
    			## the parent can be extracted from an assignment id row, as can the actual story
    			'result_assignment_ids': [ [ 'S10', 'S11' ], [ 'S12', 'S13' ] ]
    			},
    		'evaluation': {
    			'HITIds': [ 'H3244', 'H1239', 'H7426', 'H9120' ],
    			'story_assignment_ids': [ 'S10', 'S11', 'S12', 'S13' ],
    			'num_evaluations_per_story': 10,
    			
    			'result_assignment_ids': [ [ 'E101', ... ], [ 'E111', ... ], [ 'E121', ... ], [ 'E131', ... ] ]
    			}
    		'best_story_ids': [ 'S12', 'S10' ]
    		}
    
    def create_fake_first_iteration():
    	return {
    		'stories': {
    			'HITIds': [ 'H1390' ],
    			'num_stories_per_HIT': 4,
    			
    			'parent_story_ids': None,
    			'result_story_ids': [ [ 'S1', 'S2', 'S3', 'S4' ] ]
    			
    			## the parent can be extracted from an assignment id row, as can the actual story
    			'result_assignment_ids': [ [ 'S1', 'S2', 'S3', 'S4' ] ]
    			},
    		'evaluation': {
    			'HITIds': [ 'H3244', 'H1239', 'H7426', 'H9120' ],
    			'story_assignment_ids': [ 'S1', 'S2', 'S3', 'S4' ],
    			'num_evaluations_per_story': 10,
    			
    			'result_assignment_ids': [ [ 'E1', ... ], [ 'E11', ... ], [ 'E21', ... ], [ 'E31', ... ] ]
    			}
    		'best_story_ids': [ 'S12', 'S10' ]
    		}
    '''
    state['iterations'] = []
    state['PC'] = 'generate_stories'
    
    save_state_to_path( state, state_path )
    print '[Saved initial state to "%s".]' % ( state_path, )
    
    return state

def save_state_to_path( state, state_path ):
	## In case the user control-C's in the middle, move the previous state aside.
	aside_path = state_path + '.previous'
	if os.path.exists( aside_path ): os.remove( aside_path )
	if os.path.exists( state_path ): os.rename( state_path, aside_path )
	
	json.dump( state, open( state_path, 'w' ) )
	
	'''
	## This code is similar to the above code, but performs an atomic swap.
	## UPDATE: It wouldn't work on Windows: http://docs.python.org/2/library/os.html#os.rename
	
	with tmp as tempfile.NamedTemporaryFile( delete = False ):
		tmp_path = tmp.name
	    json.dump( state, tmp )
	os.rename( tmp_path, state_path )
	'''

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
    
    def prepare_to_generate_stories():
    	## Prepare for the first iteration:
        if len( state['iterations'] ) == 0:
        	state['iterations'].append( {
        		'stories': {
					'parent_story_ids': None,
					'num_stories_per_HIT': state['params']['num_initial_stories'],
					}
        		} )
        	
            state['PC'] = 'generate_stories'
            return
        ## Prepare for a later iteration:
        else:
            iter = state['iterations'][-1]
            
            truncated_story_ids = stories.truncate_and_flip_stories_for_iteration_N_of_M( iter['best_stories'], len( state['iterations'] ), state['params']['max_iterations'] )
            state['iterations'].append( {
        		'stories': {
					'parent_story_ids': truncated_story_ids,
					'num_stories_per_HIT': state['params']['num_continuing_stories'],
					}
        		} )
            
            state['PC'] = 'generate_stories'
            return
    
    def generate_stories():
        ### 1 Create the HIT for generating the stories.
        ### 2 Move into 'wait_for_stories' state.
        assert len( state['iterations'] ) > 0
        iter = state['iterations'][-1]
        
        if iter['stories']['parent_story_ids'] is None:
        	num_stories = state['params']['num_initial_stories']
        	iter['stories']['num_stories_per_HIT'] = num_stories
        	iter['stories']['HITIds'] = [ stories.create_HIT_for_generating_N_initial_stories( num_stories ) ]
        else:
        	num_stories = state['params']['num_continuing_stories']
        	iter['stories']['num_stories_per_HIT'] = num_stories
        	iter['stories']['HITIds'] = stories.create_HITs_for_continuing_stories( iter['stories']['parent_story_ids'], num_stories )
		
		## Set the number of results initially to zero.
		iter['stories']['result_assignment_ids'] = [ 0 ] * len( iter['stories']['HITIds'] )
		
        state['PC'] = 'wait_for_stories'
        return
    
    def wait_for_stories():
        ### 1 Check if all stories are in.
        ### 2 If not, sleep.
        ### 3 If so, move into create_evaluation() state.
        assert len( state['iterations'] ) > 0
        iter = state['iterations'][-1]
        
        assert 'stories' in iter
        story_data = iter['stories']
        HITIds = story_data['HITIds']
        
        missing = False
        for i, HITId in enumerate( HITIds ):
            if len( story_data['result_assignment_ids'][i] ) < story_data['num_stories_per_HIT']:
                assignment_ids = stories.get_story_AssignmentIds_for_HITId( HITId )
                story_data['result_assignment_ids'][i] = story_ids
            
            print 'Got %d/%d stories.' % ( len( story_ids ), story_data['num_stories_per_HIT'] )
            
            if len( story_data['result_assignment_ids'][i] ) < story_data['num_stories_per_HIT']:
                missing = True
        
        if missing:
            print 'Sleeping...'
            time.sleep( kSleepSeconds )
            return
        else:
            state['PC'] = 'evaluate_stories'
            return
    
    def evaluate_stories():
        ### 1 Create the HIT for evaluating the stories.
        ### 2 Move into 'wait_for_evaluations' state.
        assert len( state['iterations'] ) > 0
        iter = state['iterations'][-1]
        
        assert 'stories' in iter
        story_data = iter['stories']
        
        assert 'result_assignment_ids' in story_data
        all_story_ids = itertools.chain( *story_data['result_assignment_ids'] )
        assert len( all_story_ids ) == len( story_data['num_stories_per_HIT'] ) * ( 1 if story_data['parent_story_ids'] is None else len( story_data['parent_story_ids'] ) )
        
        HITIds = evaluation.publish_evaluations( all_story_ids, state['params']['evaluation_parameters'] )
        iter['evaluation'] = {
        	'HITIds': HITIds,
        	'story_assignment_ids': all_story_ids,
        	'num_evaluations_per_story': state['params']['evaluation_parameters']['num_evaluations_per_story']
        	}
        
        ## Set the number of results initially to zero.
		iter['evaluation']['result_assignment_ids'] = [ 0 ] * len( iter['evaluation']['HITIds'] )
		
        state['PC'] = 'wait_for_evaluations'
        return
    
    def wait_for_evaluations():
        ### 1 Check if all evaluations are in.
        ### 2 If not, sleep.
        ### 3 If so, move into create_evaluation() state.
        assert len( state['iterations'] ) > 0
        iter = state['iterations'][-1]
        
        assert 'evaluation' in iter
        evaluation_data = iter['evaluation']
        HITIds = evaluation_data['HITIds']
        
        missing = False
        for i, HITId in enumerate( HITIds ):
            if len( evaluation_data['result_assignment_ids'][i] ) < evaluation_data['num_evaluations_per_story']:
                evaluation_ids = evaluation.get_evaluation_AssignmentIds_for_HITId( HITId )
                evaluation_data['result_assignment_ids'][i] = evaluation_ids
            
            print 'Got %d/%d evaluations.' % ( len( evaluation_ids ), evaluation_data['num_evaluations_per_story'] )
            
            if len( evaluation_data['result_assignment_ids'][i] ) < evaluation_data['num_evaluations_per_story']:
                missing = True
        
        if missing:
            print 'Sleeping...'
            time.sleep( kSleepSeconds )
            return
        else:
            state['PC'] = 'keep_best_stories'
            return
    
    def keep_best_stories():
        ### 1 Create the HIT for evaluating the stories.
        ### 2 Move into 'wait_for_evaluations' state.
        assert len( state['iterations'] ) > 0
        iter = state['iterations'][-1]
        
        assert evaluation in iter
        evaluation_data = iter['evaluation']
        
        assert 'result_assignment_ids' in evaluation_data
        assert len( itertools.chain( *evaluation_data['result_assignment_ids'] ) ) == len( evaluation_data['num_evaluations_per_story'] ) * len( evaluation_data['story_assignment_ids'] )
        
        best_story_ids = evaluation.keep_N_best_stories( evaluation_data['story_assignment_ids'], evaluation_data['result_assignment_ids'], state['params']['keep_N_best_stories'] )
        iter['best_stories'] = best_story_ids
        
        if len( state['iterations'] ) == state['params']['max_iterations']:
            state['PC'] = None
            return
        else:
            state['PC'] = 'prepare_to_generate_stories'
            return
    
    ## This looks crazy, but vars() are the local variables of the function as a dictionary,
    ## state['PC'] tells us the name of the function to call,
    ## and the final parentheses call it.
    vars()[ state['PC'] ]()
	return

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
