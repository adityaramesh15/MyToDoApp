from flask import Flask, render_template, request, redirect, url_for, g
from database import db, Todo
from recommendation_engine import RecommendationEngine
from context_processors import inject_current_date
from tab import Tab
import os
import json

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "todos.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
with app.app_context():
    db.create_all()

@app.context_processor
def inject_common_variables():
    return inject_current_date()

@app.before_request
def load_data_to_g():
    todos = Todo.query.all()
    g.todos = todos
    g.todo = None
    g.TabEnum = Tab
    g.selectedTab = Tab.NONE

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/add", methods=["POST"])
def add_todo():
    todo = Todo(name = request.form["todo"])
    db.session.add(todo)
    db.session.commit()

    return redirect(url_for("index"))


@app.route("/remove/<int:id>", methods=["GET", "POST"])
def remove_todo(id):
    db.session.delete(Todo.query.filter_by(id=id).first())
    db.session.commit()
    return redirect(url_for("index"))


@app.route("/recommend/<int:id>", methods=["GET"])
@app.route("/recommend/<int:id>/<refresh>", methods=["GET"])
async def recommend(id, refresh = False):
    recommendation_engine = RecommendationEngine()
    g.todo = db.session.query(Todo).filter_by(id = id).first()
    g.selectedTab = Tab.RECOMMENDATIONS

    if g.todo and not refresh:
        try:
            if g.todo.recommendations_json is not None:
                g.todo.recommendations = json.loads(g.todo.recommendations_json)
                return render_template("index.html")
        except ValueError as e:
            print("Error: ", e)

    previous_links_str = None
    if refresh:
        g.todo.recommendations = json.loads(g.todo.recommendations_json)
        links = [item["link"] for item in g.todo.recommendations]
        previous_links_str = ", ".join(links)


    g.todo.recommendations = await recommendation_engine.get_recommendations(g.todo.name, previous_links_str)

    try:
        g.todo.recommendations_json = json.dumps(g.todo.recommendations)
        db.session.add(g.todo)
        db.session.commit()
    except Exception as e:
        print(f"Error adding and committing todo: {e}")
        return  


    return render_template("index.html")


@app.route("/details/<int:id>", methods = ["GET"])
def details(id):
    g.selectedTab = Tab.DETAILS
    g.todos = Todo.query.all()
    g.todo = Todo.query.filter_by(id=id).first()

    return render_template("index.html")

@app.route('/edit/<int:id>', methods=['GET'])
def edit(id):
    g.selectedTab = Tab.EDIT
    g.todos = Todo.query.all()
    g.todo = Todo.query.filter_by(id=id).first()

    return render_template('index.html')

@app.route('/update/<int:id>', methods=['POST'])
def update_todo(id):
    g.selectedTab = Tab.DETAILS

    if request.form.get('cancel') != None:
        return redirect(url_for('index'))
    
    name = request.form['name']
    due_date = request.form.get('duedate')
    notes=request.form.get('notes')
    priority=request.form.get('priority')
    completed=request.form.get('completed')

    todo = db.session.query(Todo).filter_by(id=id).first()
    if todo != None:
        todo.name = name

        if due_date != "None":
            todo.due_date = due_date

        if notes != None:
            todo.notes = notes

        if priority != None:
            todo.priority = int(priority) 

        if completed == None:
            todo.completed = False
        elif completed == "on":
            todo.completed = True

    db.session.add(todo)
    db.session.commit()

    return redirect(url_for("index"))

@app.route('/completed/<int:id>/<complete>', methods=['GET'])
def completed(id, complete):
    g.selectedTab = Tab.NONE
    g.todo = Todo.query.filter_by(id=id).first()
    if (g.todo != None and complete == "true"):
        g.todo.completed = True
    elif (g.todo != None and complete == "false"):
        g.todo.completed = False

    db.session.add(g.todo)
    db.session.commit()
    return redirect(url_for('index'))  


if __name__ == "__main__":
    app.run(debug=True)

