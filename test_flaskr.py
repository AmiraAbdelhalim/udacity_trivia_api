import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format('postgres', 'koko','localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

            self.new_question = {
                'question': 'How many countries are there in the region of Europe?',
                'answer': 44,
                'difficulty': 3,
                'category': 3
            }
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_paginated_questions(self):
        """test pagination"""

        response = self.client().get('/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_request_beyond_valid_page(self):
        """test pagination failure"""
        response = self.client().get('/questions?page=404')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_delete_question(self):
        """test delete question"""

        question = Question(
            question=self.new_question['question'], answer=self.new_question['answer'],
            difficulty=self.new_question['difficulty'], category=self.new_question['category']
        )

        question.insert()
        question_id = question.id

        question_before = Question.query.all()

        response = self.client().delete('/questions/{}'.format(question_id))
        data = json.loads(response.data)

        question_after = Question.query.all()

        question = Question.query.filter(Question.id==1).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], question_id)

        self.assertTrue(len(question_before) - len(question_after) == 1)
        self.assertEqual(question, None)

    def test_create_question(self):
        """test question creation"""

        question_before = Question.query.all()

        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)

        question_after = Question.query.all()

        question = Question.query.filter_by(id=data['created']).one_or_none()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(len(question_after) - len(question_before) == 1)
        self.assertIsNotNone(question)

    def test_422_question_creation_fails(self):
        """test question creation failure"""

        question_before = Question.query.all()

        response = self.client().post('/questions', json={})
        data = json.loads(response.data)

        question_after = Question.query.all()

        self.assertEqual(response.status_code, 422)
        self.assertEqual(data['success'], False)

        self.assertTrue(len(question_after) == len(question_before))

    def test_search_questions(self):
        """test search question"""

        response = self.client().post('/questions', json={'searchTerm': 'life'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertEqual(len(data['questions']), 1)

    def test_404_search_questions_fails(self):
        """test search failure"""

        response = self.client().post('/questions', json={'searchTerm': 'amira'})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_get_questions_by_category_id(self):
        """test get questions of a category"""
        response = self.client().get('/categories/1/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertNotEqual(len(data['questions']), 0)

    def test_400_get_questions_by_category_id_fails(self):
        """test get questions of a category failure"""

        response = self.client().get('/categories/400/questions')
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad Request')

    def test_play_quiz(self):
        """test play quiz"""

        response = self.client().post('/quizzes', json={
            'previous_questions': [20, 21], 'quiz_category': {'type': 'science', 'id': 1}
        })
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['success'], True)

        self.assertTrue(data['question'])
        self.assertEqual(data['question']['category'], 1)

    def test_play_quiz_fails(self):
        """test play quiz failure"""

        response = self.client().post('/quizzes', json={})
        data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Bad Request')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()