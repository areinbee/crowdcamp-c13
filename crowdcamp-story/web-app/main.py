#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import random
import logging


from google.appengine.ext import db

include_css = """
    <head>
        <link type="text/css" rel="stylesheet" href="/stylesheets/main.css" />
    </head>"""

prompt = "<h1>I've got a story in mind for you. Ask Yes/No questions to find out what the story is about!</h1>"
final_story = "<h1>Great, you're done! Here is the summary of facts in your story:</h1>"
all_stories = "<h1>All stories</h1>"
question_count = 20

original_domain = {
    "main_prompt": "I've got a story for you. Ask YES/NO questions to find out more!",
    "elements": ["the story"],
    "yes_count" : 200,
    "new_element_prompt": "Now ask about:"
}

story_domain_1 = {
    "main_prompt": "I've got a story for you. Ask questions to find out more! The questions MUST be ones that can be answered with a YES or NO. Don't worry if an answer doesn't appear, just press Enter again. ",
    "elements": ["Characters", "Setting", "Conflict", "Resolution"],
    "yes_count" : 7,
    "new_element_prompt": "Now ask about:"
    }
    
story_domain_2 = {
    "main_prompt": "Help me design a movie poster for Batman. Ask questions about the design to find out more! The questions MUST be ones that can be answered with a YES or NO. Don't worry if an answer doesn't appear, just press Enter again.",
    "elements": ["Theme", "Layout", "Images", "Text"],
    "yes_count" : 7,
    "new_element_prompt": "Now let's think about: "
    }
    
story_domain_3 = {
    "main_prompt": "Help me design a movie poster for Titanic. Ask questions about the design to find out more! The questions MUST be ones that can be answered with a YES or NO. Don't worry if an answer doesn't appear, just press Enter again.",
    "elements": ["Theme", "Layout", "Images", "Text"],
    "yes_count" : 7,
    "new_element_prompt": "Now let's think about: "
    }
    
story_domain_4 = {
    "main_prompt": "Help me design a movie poster. I've got a specific movie in mind. Ask questions to find out more! The questions MUST be ones that can be answered with a YES or NO. Don't worry if an answer doesn't appear, just press Enter again.",
    "elements": ["Theme", "Layout", "Images", "Text"],
    "yes_count" : 1,
    "new_element_prompt" : "Now let's think about: "
    }
    
story_domain_5 = {
    "main_prompt": "I've got a story for you. Ask questions to find out more! The questions MUST be ones that can be answered with a YES or NO. Don't worry if an answer doesn't appear, just press Enter again.",
    "elements": ["Once upon a time", "every day", "but one day", "because of that", "because of that", "until, finally", "and ever since then"],
    "yes_count" : 3,
    "new_element_prompt": " >> "
    }

story_domain_6 = {
    "main_prompt": "Help me design a movie poster. I've got a specific movie in mind. Ask questions to find out more! The questions MUST be ones that can be answered with a YES or NO. Don't worry if an answer doesn't appear, just press Enter again.",
    "elements": ["Design", "Audience", "Message", "Purpose"],
    "yes_count" : 7,
    "new_element_prompt" : "Now let's think about: "    
    }
    
domains = [original_domain, story_domain_1, story_domain_2, story_domain_3, story_domain_4, story_domain_5, story_domain_6]
    

div_irb = """
<div class="irb">
<p>Designing Micro-Tasks for Computer Graphics Applications and Crowdsourced Creativity

<p>INFORMED CONSENT FORM

<p>RESEARCH PROCEDURES:
This research is being conducted to design micro-tasks for computer graphics applications and study crowdsourced creativity. If you agree to participate, you will be asked to complete the HIT shown below.

<p>RISKS:
There are no foreseeable risks for participating in this research.

<p>BENEFITS:
There are no benefits to you as a participant other than to further research in computer graphics.

<p>CONFIDENTIALITY:
This research is anonymous. (1) Your name will not be included on the surveys and other collected data; (2) a code unrelated to your Worker ID will be placed on the survey and other collected data; (3) through the use of an identification key, the researcher will be able to link your survey to your Amazon Worker ID; and (4) only the researcher will have access to the identification key.

<p>PARTICIPATION:
Your participation is voluntary, and you may withdraw from the study at any time and for any reason. If you decide not to participate or if you withdraw from the study, there is no penalty or loss of benefits to which you are otherwise entitled. There are no costs to you or any other party. You will be paid the advertised amount for your completion of the HITs.

<p>CONTACT:
This research is being conducted by Yotam Gingold from the Department of Computer Science at George Mason University. He may be reached at 703-993-9196 or <a href="mailto:ygingold@cs.gmu.edu">ygingold@cs.gmu.edu</a> for questions or to report a research-related problem. You may contact the George Mason University Office of Research Integrity &amp; Assurance at 703-993-4121 if you have questions or comments regarding your rights as a participant in the research. This research has been reviewed according to George Mason University procedures governing your participation in this research.

<p>CONSENT:
By accepting this HIT, you acknowledge that you have read this form and agree to participate in this study.
If you do not agree with the consent form and wish not to participate in this study, please skip this HIT.
</div>
"""

class Story(db.Model):
    user = db.StringProperty()
    curr_element_id = db.IntegerProperty()
    yes_count = db.IntegerProperty()
    domain_id = db.IntegerProperty()

class Question(db.Model):
    question = db.StringProperty()
    answer = db.StringProperty()
    user = db.StringProperty()
    story = db.ReferenceProperty(Story)
    q_id = db.IntegerProperty()
    element = db.StringProperty()
    
    def display(self, response):
        prefix = ""
        if self.element is not None:
            prefix = "<i>[%s]</i> " % self.element
        elif self.q_id is not None:
            prefix = "(%d)" % self.q_id         
   
   
        response.out.write('<h2 class="%s">%s %s <span class="answer">%s</span></h2>' % (self.answer, prefix, self.question, self.answer) )
        
class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(include_css)
        self.response.out.write("""
            <h2>Story Oracle</h2>
            <h1><a href="new?domainId=0">Original</a></h1>
            <h1><a href="new?domainId=1">Story with structure: character/setting/conflict/resolution</a></h1>
            <h1><a href="new?domainId=5">Story with structure: once upon a time, until one day, and because of that, until finally...</a></h1>
            <h1><a href="new?domainId=6">Mystery movie poster</a></h1>
            <h1><a href="new?domainId=2">Movie poster: Batman</a></h1>
            <h1><a href="new?domainId=3">Movie poster: Titanic</a></h1>
        """)
        
class NewStoryHandler(webapp2.RequestHandler):
    def get(self):
        s = Story()
        s.user = self.request.get('user')
        s.yes_count = 0
        s.curr_element_id = 0
        if self.request.get('domainId') is not None :
            s.domain_id = int(self.request.get('domainId'))
        s.put()
        self.redirect('/editstory/%s?%s' % (s.key(), self.request.query_string))
        
       
    
class EditStoryHandler(webapp2.RequestHandler):
    def get(self, story_id):
        logging.info("i am logging some stuff!")
        logging.info(self.request.get('assignmentId'))
        self.response.out.write(include_css)
        
        if self.request.get('assignmentId') == "ASSIGNMENT_ID_NOT_AVAILABLE":
            self.response.out.write(div_irb)
        
        domainId=0;
        if self.request.get('domainId') is not None :
            domainId = int(self.request.get('domainId'))
            
        prompt = "<h1>%s</h1>" % domains[domainId]["main_prompt"]
        self.response.out.write(prompt)

        questions = Question.all()
        s = Story.get(story_id)
        
        num_elements = len(domains[s.domain_id]['elements'])
        logging.info("len of elements %d" % len(domains[s.domain_id]['elements']))
        if s.curr_element_id >= len(domains[s.domain_id]['elements']):
            self.redirect('/story/%s?%s' % (story_id, self.request.query_string))
        
        questions.filter("story =", s)
        questions.order('q_id')
        for question in questions:
            question.display(self.response)
             
        curr_element = domains[int(s.domain_id)]['elements'][int(s.curr_element_id)]
                
        questions_remaining = question_count - questions.count()
        question_id = questions.count() + 1
        
        self.response.out.write("<h1>Type your YES/NO question about <i>%s</i>:</h1>"%curr_element)
        
        if self.request.get('assignmentId') == "ASSIGNMENT_ID_NOT_AVAILABLE":
            self.response.out.write("""
                <form action="/answer_q" method="post">
                    <div>
                    
                    <input type="text" name="question" size="90"></input>
                    </div>
                    <br />
                    <div><input type="submit" value="You must accept the HIT" disabled></div>
                </form>""")

        else:         
            self.response.out.write("""
                <form action="/answer_q?%s" method="post">
                    <div>
                    <input type="text" name="question" size="90" autofocus></input>
                    </div>
                    <br />
                    <div><input type="submit" value="Ask"></div>
                    <input type="hidden" name="story_id" value="%s" />
                    <input type="hidden" name="question_id" value="%s" />
                    <br />
                    <br />
                    <br />
                    <a href="/story/%s?%s">I've reached the end!</a>  
                </form>"""
                % (self.request.query_string, story_id, question_id, story_id, self.request.query_string))
            
class StoryHandler(webapp2.RequestHandler):
    def get(self, story_id):
        assignmentId = self.request.get('assignmentId')
        formAction = self.request.get('turkSubmitTo')
        
        self.response.out.write(include_css)
        self.response.out.write(final_story)

        questions = Question.all()
        questions.filter("story =", Story.get(story_id))
        questions.order('q_id')
        for question in questions:
            question.display(self.response)
            
        self.response.out.write("""
            <form action="%s/mturk/externalSubmit" method="post">
                <div>
                <h1>How was this experience? Leave us feedback (optional)</h1>
                <textarea name="feedback" rows="5" cols="50" autofocus></textarea>
                </div>
                <br />
                <input type="hidden" name="assignmentId" value="%s" />
                <div><input type="submit" name="submit" value="Submit"></div>
            </form>""" 
            % (formAction, assignmentId))

class AllStoriesHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(include_css)
        self.response.out.write(all_stories)

        stories = Story.all()
        stories.order('-__key__')
        for story in stories:
            questions = Question.all()
            questions.filter("story =", story)
            questions.order('q_id')
            if questions.count() > 0:
                self.response.out.write("<hr />")
                self.response.out.write("<h1>Another Story</h1>")          
    
                for question in questions:
                    question.display(self.response)

class AnswerQuestion(webapp2.RequestHandler):
    def post(self):
        story_id = self.request.get('story_id')

        if self.request.get('question') != "":
            q = Question()
            q.question = self.request.get('question')
            q.story = Story.get(story_id)
            q.q_id = int(self.request.get('question_id'))
            q.element = domains[q.story.domain_id]['elements'][q.story.curr_element_id]
            if random.random() < .5:
                q.answer = "yes"
                q.story.yes_count+=1
                if q.story.yes_count > domains[q.story.domain_id]['yes_count']:
                    q.story.curr_element_id += 1
                    q.story.yes_count = 0
                q.story.put()
            else:
                q.answer = "no"
                
            q.put()
            
            if q.story.curr_element_id >= len(domains[q.story.domain_id]['elements']):
                self.redirect('/story/%s?%s' % (story_id, self.request.query_string))

        self.redirect('/editstory/%s?%s' % (story_id, self.request.query_string))


        
app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/new', NewStoryHandler),
    ('/editstory/([^/]+)', EditStoryHandler),
    ('/story/([^/]+)', StoryHandler),
    ('/answer_q', AnswerQuestion),
    ('/all_stories', AllStoriesHandler),
], debug=True)

def main():
    # Set the logging level in the main function
    # See the section on Requests and App Caching for information on how
    # App Engine reuses your request handlers when you specify a main function
    logging.getLogger().setLevel(logging.DEBUG)
    webapp.util.run_wsgi_app(app)

if __name__ == '__main__':
    main()
