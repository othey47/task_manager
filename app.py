from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

tasks = {
    "Title" : "Create Web application",
    "Description" : "I need to finish the assignments before the ending of this month.",
    "Priority" : 'High'
}

@app.route('/')
def main():
    total = 0
    pending = 0
    completed = 0
    return render_template("index.html", total=total, pending=pending, completed=completed)

@app.route('/view_tasks',)
def view_tasks():
    message = "Welcome to view task."
    return render_template("view.html", message=message, tasks=tasks)






if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)