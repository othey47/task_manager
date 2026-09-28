from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

tasks = {

}

@app.route('/')
def main():
    total = 0
    pending = 0
    completed = 0
    return render_template("index.html", total=total, pending=pending, completed=completed)

@app.route('/view_tasks')
def view_tasks():
    message = "Welcome to view task."

    return render_template("view.html", message=message, tasks=tasks)

@app.route('/add_tasks', methods=['GET','POST'])
def add_tasks():

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority')


        tasks['title'] = title
        tasks['description'] = description
        tasks['priority'] = priority

        return redirect('/view_tasks')    

    return render_template('add.html')

@app.route('/edit_tasks', methods=['GET','POST'])
def edit_tasks():
    if request.method == 'POST':
        new_title = request.form.get('title')
        new_description = request.form.get('description')
        new_priority = request.form.get('priority')

        if new_title:
            tasks['title'] = new_title
        
        if new_description:
            tasks['description'] = new_description

        if new_priority:
            tasks['priority'] = new_priority


        return redirect("/view_tasks")
    
    return render_template('edit.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)