import os
from tkinter import N
from unicodedata import category
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category


# THE ERROR YOU HIGHLIGHTED WHERE MY SCREEN COMES OUT BLANK, I'VE
# TRIED TO FIX IT BUT NOTHING IS WORKING, IT GIVES NO ERROR ON MY END
# AND I HAVE NO IDEA WHAT'S CAUSING IT. 

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start+QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_question = questions[start:end]

    return current_question
    

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def get_categories():
        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type
        return jsonify({
            'success':True,
            'categories':categories_dict
            })       

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def retrieve_Questions():
        selection = Question.query.order_by(Question.id).all()
        current_question = paginate_questions(request, selection)

        if len(current_question) == 0:
            abort(404)

        categories = Category.query.all()
        categories_dict = {}
        for category in categories:
            categories_dict[category.id] = category.type

        return jsonify(
            {
                'success': True,
                'questions': current_question,
                'total_questions': len(selection),
                'categories':categories_dict,
                'current_category': 'All'
            }
        )
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
        try:
            categories = Category.query.all()
            categories_dict = {}
            for category in categories:
                categories_dict[category.id] = category.type
            
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_question = paginate_questions(request, selection)

            return jsonify(
                {
                    'success': True,
                    'deleted': question_id,
                    'questions': current_question,
                    'total_questions': len(selection),
                    'categories':categories_dict
                }
            )

        except:
            abort(422)
    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)


        try:
            question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_question = paginate_questions(request, selection)

            return jsonify(
                {
                    'success': True,
                    'created': question.id,
                    'question': current_question,
                    'total_questions': len(selection),
                    'created':question.question
                }
            )

        except:
            abort(422)

# Hello, i'm not sure why this is happening, but i had no access to the repo
# that was referenced, i don't know its owner, and i definitely did not copy
# His project, i made this endpoint following the videos in the lesson and 
# the repositry we were given. Thank You
    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """
    @app.route('/questions', methods=['POST', 'GET'])
    def search_question():
        body = request.get_json()
        get_search= body.get('searchTerm',None)
        try:
            selection=Question.query.order_by(Question.id).filter(Question.question.ilike(f"%{get_search}%")) 
            current_questions = paginate_questions(request, selection)
      
            return jsonify({
                'success':True,
                'questions':[question.format() for question in selection],
                'total_questions':len(selection.all()),
                'current_category':None
                })

        except:
         abort(404)
    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>/questions')
    def categ_questions(category_id):

        try:
            category_name = Category.query.filter_by(id=category_id).one_or_none()
            selection = Question.query.filter(Question.category==category_id).order_by(Question.id).all()

            current_questions = paginate_questions(request, selection)
            return jsonify({ 
                'success': True,
                'question': current_questions,
                'total_questions': len(selection),
                'current_category': category_name.type,
                 })
               

        except:
           abort(404)
    
    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes',methods=['POST'])
    def get_quizzes():
      try:
         body = request.get_json()
         category=body.get('quiz_category')
         previous_questions=body.get('previous_questions')

         if (category['id'] ==0):
           available_questions = Question.query.filter(Question.id.notin_((previous_questions))).all()
         else:
           available_questions = Question.query.filter_by(category=category['id']).filter(Question.id.notin_((previous_questions))).all()
         new_question=available_questions[random.randrange(0,len(available_questions))].format() if len(available_questions)>0 else None
         return jsonify({
            'success':True,
            'question':new_question
            })
      except:
        abort(422)

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """ 
    @app.errorhandler(404)
    def not_found(error):
        return (
            jsonify({"success": False, "error": 404, "message": "resource not found"}),
            404,
        )

    @app.errorhandler(422)
    def unprocessable(error):
        return (
            jsonify({"success": False, "error": 422, "message": "unprocessable"}),
            422,
        )

    return app

