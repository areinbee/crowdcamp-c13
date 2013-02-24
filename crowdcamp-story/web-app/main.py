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

class Story(db.Model):
    user = db.StringProperty()

class Question(db.Model):
    question = db.StringProperty()
    answer = db.StringProperty()
    user = db.StringProperty()
    story = db.ReferenceProperty(Story)
    q_id = db.IntegerProperty()
    
    def display(self, response):
        logging.info(self.q_id)
        if self.q_id is None:   
            response.out.write('<h2 class="%s">%s <span class="answer">%s</span></h2>' % (self.answer, self.question, self.answer) )
        else:
            response.out.write('<h2 class="%s">(%d) %s <span class="answer">%s</span></h2>' % (self.answer, self.q_id, self.question, self.answer) )

class MainHandler(webapp2.RequestHandler):
    def get(self):
        s = Story()
        s.user = self.request.get('user')
        s.put()
        self.redirect('/editstory/%s' % s.key())
       
    
class EditStoryHandler(webapp2.RequestHandler):
    def get(self, story_id):
        self.response.out.write(include_css)
        self.response.out.write(prompt)

        questions = Question.all()
        questions.filter("story =", Story.get(story_id))
        questions.order('q_id')
        for question in questions:
            question.display(self.response)
    
        questions_remaining = question_count - questions.count()
        #if questions_remaining == 0:
        #    self.redirect('/story/%s' % story_id)
        question_id = questions.count() + 1
        
        self.response.out.write("""
            <form action="/answer_q" method="post">
                <div>
                <h1>Type your YES/NO question:</h1>
                <input type="text" name="question" size="90"></input>
                </div>
                <br />
                <div><input type="submit" value="Ask"></div>
                <input type="hidden" name="story_id" value="%s" />
                <input type="hidden" name="question_id" value="%s" />
                <br />
                <br />
                <br />
                <a href="/story/%s">I've reached the end!</a>  
            </form>"""
            % (story_id, question_id, story_id))
            
class StoryHandler(webapp2.RequestHandler):
    def get(self, story_id):
        self.response.out.write(include_css)
        self.response.out.write(final_story)
        self.response.out.write("<h2>Story ID: <span class='key'>%s</span></h2>" % story_id)

        questions = Question.all()
        questions.filter("story =", Story.get(story_id))
        for question in questions:
            question.display(self.response)

class AllStoriesHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write(include_css)
        self.response.out.write(all_stories)

        stories = Story.all()
        for story in stories:
            self.response.out.write("<hr />")
            self.response.out.write("<h1>Another Story</h1>")          
            questions = Question.all()
            questions.filter("story =", story)
            for question in questions:
                question.display(self.response)

class AnswerQuestion(webapp2.RequestHandler):
    def post(self):
        story_id = self.request.get('story_id')
        q = Question()
        q.question = self.request.get('question')
        q.story = Story.get(story_id)
        q.q_id = int(self.request.get('question_id'))
        if random.random() < .5:
            q.answer = "yes"
        else:
            q.answer = "no"
            
        q.put()

        self.redirect('/editstory/%s' % story_id)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
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
