from flask import Flask, request, render_template, redirect, url_for

from forms import TodoForm
from models import books

from flask import Flask, jsonify
from models import books
from models import api
from flask import abort
from flask import make_response
from flask import request

app = Flask(__name__)
app.config["SECRET_KEY"] = "nininini"

#FORMS responsible functions

@app.route("/books/", methods=["GET", "POST"])
def books_list():
    form = TodoForm()
    error = ""
    if request.method == "POST":
        if form.validate_on_submit():
            try:
                updated_fd = form.data
                updated_fd['id'] = books.all()[-1]['id'] + 1
                books.create(updated_fd)
                books.save_all() 
            except:
                updated_fd = form.data
                updated_fd['id'] = 1
                books.create(updated_fd)
                books.save_all()
  
        return redirect(url_for("books_list"))
    return render_template("books.html",form=form, books=books.all(), error=error)

@app.route("/book/<int:book_id>/", methods=["GET", "POST"])
def book_details(book_id):
    book = books.get(book_id - 1)
    form = TodoForm(data=book)

    if request.method == "POST":
        if form.validate_on_submit():
            books.update(book_id - 1, form.data)
        return redirect(url_for("books_list"))
    return render_template("book.html", form=form, book_id=book_id)

#API responsible functions
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found', 'status_code': 404}), 404)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': 'Bad request', 'status_code': 400}), 400)

@app.route("/api/v1/books/", methods=["POST"])
def create_book():
    if not request.json or not 'title' in request.json:
        abort(400)
    book = {
        'id': books.all()[-1]['id'] + 1,
        'title': request.json['title'],
        'description': request.json.get('description', ""),
        'done': False,
        'date': request.json.get('date', ""),
        'genre': request.json.get('genre', "")
    }
    api.create_api(book)
    return jsonify({'book': book}), 201

@app.route("/api/v1/books/", methods=["GET"])
def books_list_api_v1():
    return jsonify(books.all())

@app.route("/api/v1/books/<int:book_id>", methods=["GET"])
def get_book(book_id):
    book = api.get_api(book_id)
    if not book:
        abort(404)
    return jsonify({"book": book})

@app.route("/api/v1/books/<int:book_id>", methods=['DELETE'])
def delete_book(book_id):
    print(book_id)
    result = api.delete_api(book_id)
    if not result:
        abort(404)
    return jsonify({'result': result})

@app.route("/api/v1/books/<int:book_id>", methods=["PUT"])
def update_book(book_id):
    book = books.get(book_id)
    if not books:
        abort(404)
    if not request.json:
        abort(400)
    data = request.json
    if any([
        'title' in data and not isinstance(data.get('title'), str),
        'description' in data and not isinstance(data.get('description'), str),
        'done' in data and not isinstance(data.get('done'), bool)
    ]):
        abort(400)
    book = {
        'title': data.get('title', book['title']),
        'description': data.get('description', book['description']),
        'done': data.get('done', book['done'])
    }
    api.update_api(book_id, book)
    return jsonify({'book': book})

if __name__ == "__main__":
    app.run(debug=True)

