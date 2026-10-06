from flask import Flask, render_template, redirect, url_for, request

app = Flask(__name__)

tasks = []
priorities = ['Low', 'Medium', 'High']

def get_id(tasks):
    return int(len(tasks)+1)

@app.route('/')
def main():
    total = 0
    pending = 0
    completed = 0
    return render_template("index.html", total=total, pending=pending, completed=completed)

@app.route('/view_tasks')
def view_tasks():
    return render_template("view.html", tasks=tasks)

@app.route('/add_tasks', methods=['GET','POST'])
def add_tasks():

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        priority = request.form.get('priority') or 'Low'

        id = get_id(tasks)

        tasks.append({
            "id" : id,
            "title" : title,
            "description" : description,
            "priority" : priority,
            "status" : "pending"

        })

        return redirect(url_for('view_tasks'))    

    return render_template('add.html', priorities=priorities)


@app.route('/edit_tasks', methods=['GET','POST'])
def edit_tasks():
    
    id = int(request.args.get('id'))
    
    print("ID:", id)
    print("TASKS:", tasks)

    if request.method == 'POST':
    
        for task in tasks:
            if task['id'] == id:
                new_title = request.form.get('title')
                new_description = request.form.get('description')
                new_priority = request.form.get('priority')

                
                if new_title:
                    task['title'] = new_title
                if new_description:
                    task['description'] = new_description
                if new_priority:
                    task['priority'] = new_priority

        return redirect(url_for("view_tasks"))
    
    for task in tasks:
        if task['id'] == id:
            return render_template('edit.html', id=id, task=task, priorities=priorities)

@app.route('/delete_tasks', methods=['POST'])
def delete_tasks():
    id = int(request.form.get('id'))

    for task in tasks:
        if task['id'] == id:
            tasks.remove(task)

    return redirect(url_for('view_tasks'))

@app.route('/check_tasks', methods=['POST'])
def status():
    id = int(request.form.get('id'))

    for task in tasks:
        if task['id'] == id:
            if task['status'] == "completed":
                task.update({"status" : 'pending'})
            else:
                task.update({'status': "completed"})

    return redirect(url_for('view_tasks'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)