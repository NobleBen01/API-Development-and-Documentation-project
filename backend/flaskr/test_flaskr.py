import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = 'postgresql://postgres:09030993500@localhost/trivia'
        setup_db(self.app, self.database_path)

        self.new_question = {'question': 'Who is the richest man in Nigeria?', 'answer': 'Aliko Dangote', 'difficulty': 2, 'category': 4}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """

    def test_get_paginated_questions_without_catgory(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_beyond_valid_page(self):
        res = self.client().get('/questions?page=500')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'resource not found')


    def test_questions_within_category(self):
        res = self.client().get('/questions', json={'categories': 'Science'})
        data = json.loads(res.data)
  
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_get_categories_success(self):
        res=self.client().get('/categories')
        data=json.loads(res.data)

        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_get_categories_failure(self):
        res=self.client().get('/categories/99999')
        data=json.loads(res.data)
        
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)        
        self.assertTrue(data['message'], 'reource not found')
    
    def test_questions_nonexisting_category(self):
        res = self.client().get('/questions', json={'categories': 'Music'})
        data = json.loads(res.data)
  
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'], 0)
        self.assertTrue(len(data['questions']))


    def test_delete_question_success(self):
        question=Question(question='new question',answer= 'new answer',difficulty=1,category=1)
        question.insert()
        q_id=question.id
        res=self.client().delete(f'/questions/{q_id}')
        data=json.loads(res.data)
        question=Question.query.filter(Question.id==q_id).one_or_none()
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['deleted'],q_id)
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(question,None)

    def test_delete_question_failure(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')


    def test_422_question_creation_not_allowed(self):
        new_question= {
        'question':'new question',
        'answer':'new answer',
        'difficulty':3,
        'category':100
        }
        res = self.client().post('/questions', json=new_question)
        data = json.loads(res.data)
  
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_new_question(self):
        new_question= {
        'question':'new question',
        'answer':'new answer',
        'difficulty':3,
        'category':3
        }
        previous_total = len(Question.query.all())
        res = self.client().post('/questions',json=new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertEqual(data['total_questions'],previous_total+1)

    def test_get_question_search_with_results(self):
        search= {'searchTerm':'which'}
        res = self.client().post('/questions',json=search)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])

    # def test_get_question_search_without_results(self):
    #     search= {'searchTerm':''}
    #     res = self.client().post('/questions',json=search)
    #     data = json.loads(res.data)
    #     self.assertEqual(res.status_code,404)
    #     self.assertEqual(data['success'],False)
    #     self.assertTrue(data['message'], 'Not Found')

    def test_get_question_by_category(self):
        res = self.client().get('/categories/4/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['current_category'])

    def test_404_if_unable_get_question_by_category(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code,404)
        self.assertEqual(data['success'],False)
        self.assertTrue(data['message'],"Not Found")

    def test_get_quiz(self):
        quiz={'quiz_category':{'type':'Entertainment','id':2},'previous_questions':[4,6]}
        res = self.client().post('/quizzes',json=quiz)
        data = json.loads(res.data)
        self.assertEqual(res.status_code,200)
        self.assertEqual(data['success'],True)
        self.assertTrue(data['question'])
    
    def test_422_get_quiz(self):
        res = self.client().post('/quizzes',json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code,422)
        self.assertEqual(data['success'],False)
        self.assertTrue(data['message'],"Unable to Process")


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()