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
