from boto.mturk.connection import MTurkConnection
from boto.mturk.question import QuestionContent,Question,ExternalQuestion,QuestionForm,Overview,AnswerSpecification,SelectionAnswer,FormattedContent,FreeTextAnswer
from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement, NumberHitsApprovedRequirement, LocaleRequirement

# assumes that you have your .boto file set up in your home directory with values of
# question_form_answer and aws_secret_access_key specified
 
 
HOST = 'mechanicalturk.sandbox.amazonaws.com'
 
mtc = MTurkConnection(host=HOST)
#mtc = MTurkConnection()
 
title = 'Help us design a mobile application to transform how people\'s experience with food'
description = ('In this HIT you will help us explore ideas for how mobile technology might transform our food experience.')
keywords = 'design,creativity,food,idea'

# Set qualifications
qualifications = Qualifications()
qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value="95"))
qualifications.add(NumberHitsApprovedRequirement(comparator="GreaterThan", integer_value="500"))
qualifications.add(LocaleRequirement('EqualTo', 'US'))
 
#---------------  BUILD QUESTION 1 -------------------
 
q1 = ExternalQuestion("http://kgajos.eecs.harvard.edu/crowdcamp/eval/eval.php", 600)
 
 

#--------------- CREATE THE HIT -------------------
 
mtc.create_hit(question=q1,
               max_assignments=4,
               title=title,
               description=description,
               keywords=keywords,
               duration = 60*60,
               qualifications=qualifications,
               reward=0.5)
