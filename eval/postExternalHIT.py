from boto.mturk.connection import MTurkConnection
from boto.mturk.question import QuestionContent,Question,ExternalQuestion,QuestionForm,Overview,AnswerSpecification,SelectionAnswer,FormattedContent,FreeTextAnswer
from boto.mturk.qualification import Qualifications, PercentAssignmentsApprovedRequirement, NumberHitsApprovedRequirement, LocaleRequirement
from sys import argv  
import json

# ------- class HIT --------
# TODO: Make it possible to download HIT specification from json file
class ExternalHit:
  def __init__(self, hitSpecFile=None):
    if hitSpecFile is not None:
      self.spec = json.loads(open(hitSpecFile).read())

  def getQuestion(self):
    spec = self.spec
    return ExternalQuestion(spec['url'],
                            spec['frameHeight']) 

  def getQualification(self):
    pass


# assumes that you have your .boto file set up in your home directory with values of
# question_form_answer and aws_secret_access_key specified

# SET THESE VARIABLES
runInSandbox = False
totalNumberOfAssignments = 4*8
urlOfEvalScript = "http://kgajos.eecs.harvard.edu:8888/crowdcamp-c13/eval/eval.php"




SANDBOX_HOST = 'mechanicalturk.sandbox.amazonaws.com'
mtc = MTurkConnection(host=SANDBOX_HOST)

if not runInSandbox:
    mtc = MTurkConnection()
    urlOfEvalScript += "?destination=production"
 
title = 'Help us evaluate creative stories'
description = 'In this HIT you will be shown a short story and asked to evaluate it.'
keywords = 'creativity,stories'

# Set qualifications
qualifications = Qualifications()
if not runInSandbox:
    qualifications.add(PercentAssignmentsApprovedRequirement(comparator="GreaterThan", integer_value="95"))
    qualifications.add(NumberHitsApprovedRequirement(comparator="GreaterThan", integer_value="500"))
    qualifications.add(LocaleRequirement('EqualTo', 'US'))
 
#---------------  BUILD QUESTION 1 -------------------
 
q1 = ExternalQuestion(urlOfEvalScript, 600)
 

#--------------- CREATE THE HIT -------------------
 
mtc.create_hit(question=q1,
               max_assignments=totalNumberOfAssignments,
               title=title,
               description=description,
               keywords=keywords,
               duration = 60*60,
               qualifications=qualifications,
               reward=0.5)


if __name__ == '__main__':
  pass
