import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]

  return questions[start:end]

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  '''
  Set up CORS. Allow '*' for origins.
  '''
  CORS(app, resources={r"/api/*" : {"origins": "*"}})
  


  '''
  Use the after_request decorator to set Access-Control-Allow
  '''
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    return response
  
  '''
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_categories():
    categories = Category.query.all()

    if not categories:
      abort(404)
    else:
      return jsonify({
        'success' : True,
        'categories' : {category.id : category.type for category in categories},
        'total_categories' : len(categories)
      })

  '''
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    questions = Question.query.all()
    formatted_questions = paginate_questions(request, questions)

    categories = Category.query.all()

    if not formatted_questions:
      abort(404)
    else:
      return jsonify({
        'success' : True,
        'questions' : formatted_questions,
        'total_questions' : len(questions),
        'categories' : {category.id : category.type for category in categories},
        'current_category' : None
      })


  '''
  Create an endpoint to DELETE question using a question ID. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try: 
      question = Question.query.get(question_id)
      question.delete()

      selection = Question.query.order_by(Question.id).all()
      questions = paginate_questions(request, selection)

      return jsonify({
          'success' : True,
          'deleted' : question_id,
          'questions' : questions,
          'total_questions' : len(selection),
          'categories' : [category.format() for category in Category.query.all()],
          'current_category' : None
        })
    except:
      abort(422)


  '''
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.
  '''
  '''
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)
    search = body.get('searchTerm', None)

    try:
      if not new_question and not new_answer and not new_category and not new_difficulty:
        if not search:
          abort(422)
        selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(search)))
        questions = paginate_questions(request, selection)

        return jsonify({
          'success' : True,
          'questions' : questions,
          'total_questions' : len(selection.all()),
          'current_caterogy' : None
        })
      else:
        if not new_question or not new_answer or not new_category or not new_difficulty:
          abort(422)
        question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
        question.insert()

        selection = Question.query.order_by(Question.id).all()
        questions = paginate_questions(request, selection)

        return jsonify({
          'success' : True,
          'created' : question.id,
          'questions' : questions,
          'total_questions' : len(selection)
        })
    except:
      abort(422)


  '''
  Create a GET endpoint to get questions based on category. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_from_category(category_id):
    try:
      category = Category.query.filter(Category.id == str(category_id)).all()
      if not category:
        abort(404)
      else: 
        selection = Question.query.filter(Question.category == str(category_id)).all()
        questions = paginate_questions(request, selection)

        return jsonify({
          'success' : True,
          'questions' : questions,
          'total_questions' : len(selection),
          'current_category' : category_id
        })
    
    except:
      abort(404)
      


  '''
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 
  '''
  @app.route('/quizzes', methods=['POST'])
  def get_questions_quiz():
    body = request.get_json()

    previous_question = body.get('previous_questions', None)
    category = body.get('quiz_category', None)

    if not category:
      abort(404)
    else:

      if category['type'] == 'click':
        questions = Question.query.filter(Question.id.notin_(previous_question)).all()
      else:
        questions = Question.query.filter(Question.category == category['id']).filter(Question.id.notin_(previous_question)).all()
      
      if not questions:
        next_question = None
      else:
        next_question = questions[random.randrange(0, len(questions))].format()
      
      return jsonify({
        'success' : True,
        'question' : next_question
      })

      
  '''
  Create error handlers for all expected errors 
  '''
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success' : False,
      'error' : 400,
      'message' : 'bad request'
    }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success' : False,
      'error' : 404,
      'message' : 'resource not found'
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success' : False,
      'error' : 422,
      'message' : 'unprocessable'
    }), 422


  return app

    
