# Import the tools we need from Flask
import database
from flask import Flask, render_template, redirect, url_for, request, abort

# Create the Flask application
app = Flask(__name__)

# Database Initialization::
database.init_db()


# Create an empty list to store tasks
tasks = []

# Define the available priority levels for tasks
priorities = ['Low', 'Medium', 'High']


def count_status(tasks):

    # Initialize counters for each task status
    pending = 0
    completed = 0

    # Check whether the tasks list is not empty
    if tasks:
        # Loop through each task in the list
        for task in tasks:
            # Check if the current task is completed
            if task['status'] == 'completed':
                completed += 1
            # If the task is not completed, count it as pending
            else:
                pending += 1
    # Return both counters: pending first, completed second
    return (pending, completed)

# -- Validation func:
def valid_title(title):

    # Check if the title is empty
    if not title:
        message = f"title is empty."
        return False, message
        
    # Check if the title contains only digits or starts with a character that is not a letter
    if title.isdigit() or not title[0].isalpha():
        message = f"Title need to be Alphabitic."
        return False, message

    # Check whether the title exceeds the maximum length of 50 characters
    if len(title) > 50:
        message = f"Title is too long. Maximum 50 characters."
        return False, message

    # If all validation checks pass, indicate success
    return True, None

def valid_description(description):

    # Check whether the description exceeds the maximum length of 500 characters
    if len(description) > 500:
        message = f"Description is too long, Maximum 500 characters." 
        return False, message
    
    # If the description passes validation, indicate success
    return True, None

def valid_priority(priority):

    # Check whether the selected priority is in the list of allowed priorities
    if not priority in priorities:
        # Create an error message if the priority is not allowed
        message = f"Priorities is not include."
        return False, message
    return True, None


# --- Core function:
# Define the main route (homepage) of the application
@app.route('/')
def main():

    # Count the total number of tasks in the list
    total = len(tasks)

    # Get the number of pending and completed tasks
    values = count_status(tasks)

    # Unpack the returned tuple into two variables
    # The first value is pending tasks, and the second is completed tasks
    pending ,completed = values

    return render_template(
        "index.html", 
        total=total, 
        pending=pending, 
        completed=completed
    )

# Define the route for displaying all tasks.
@app.route('/view_tasks')
def view_tasks():

    # Open a connection to the SQLite database.
    connect = database.get_db_connection()

    # Retrieve all tasks from the tasks table.
    tasks = connect.execute("SELECT * FROM tasks").fetchall()

    # Close the database connection.
    connect.close()

    # Pass the retrieved tasks to the HTML template.
    return render_template("view.html", tasks=tasks)


# Define the route for adding a new task.
# Allow both GET (display the form) and POST (submit the form) requests.
@app.route('/add_tasks', methods=['GET','POST'])
def add_tasks():

    # Check whether the user submitted the form
    if request.method == 'POST':

        # Get the submitted values from the form
        # strip() removes whitespace from the beginning and end
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority')


        # Input Validation:
        # 1. validate title
        result, message = valid_title(title)

        # If the title is invalid, return the form with an error message
        # Pass the submitted values back so the user doesn't lose their input
        if not result:
            return render_template(
                'add.html',
                priorities=priorities,
                error=message,
                title=title,
                description=description,
                selected_priority=priority
            )

        # 2. validate the description:   
        result, message = valid_description(description)

        # If the description is invalid, return the form with an error message
        if not result:
            return render_template(
                'add.html',
                priorities=priorities,
                error=message,
                title=title,
                description=description,
                selected_priority=priority
            )
        
        # 3. validate the priority:
        result, message = valid_priority(priority)

        # If the priority is invalid, return the form with an error message
        if not result:
            return render_template(
                'add.html',
                priorities=priorities,
                error=message,
                title=title,
                description=description,
                selected_priority=priority
            )

        # Open a connection to the SQLite database.
        connect = database.get_db_connection()

        # Insert a new task into the tasks table.
        # The ? placeholders are replaced by the values in the tuple.
        connect.execute(
            "INSERT INTO tasks(title, description, priority) VALUES(?,?,?)",
            (title, description, priority)
        )

        # Save the changes to the database.
        connect.commit()
        # Close the database connection.
        connect.close()

        # Redirect the user to the page displaying all tasks
        return redirect(url_for('view_tasks'))    
    
    # If the request is GET, display the empty Add Task form
    return render_template('add.html', priorities=priorities)


# Define the route for editing a task.
# Allow GET requests to display the form and POST requests to submit changes.
@app.route('/edit_tasks', methods=['GET', 'POST'])
def edit_tasks():

    # Open a connection to the SQLite database.
    connect = database.get_db_connection()
    
    # Get the task ID from the URL query parameter
    id = int(request.args.get('id'))

    # Retrieve the task matching the ID.
    task = connect.execute(" SELECT * FROM tasks WHERE id = ? ", (id,)).fetchone()    

    # Check whether the task exists.
    if task is None:
        connect.close()
        return "Task not found", 404

    # Check whether the user submitted the edit form
    if request.method == 'POST':
                
        # Get the submitted values from the form
                
        new_title = request.form.get('title', '').strip()
        new_description = request.form.get('description', '').strip()
        new_priority = request.form.get('priority')

        # 1. Validate the title:
        if new_title:
            result, message = valid_title(new_title)

            # If validation fails, return the edit form with an error
            # and preserve the user's submitted values
            if not result:
                connect.close()
                return render_template(
                    'edit.html',
                    task=task,
                    id=id,                        priorities=priorities,
                    error=message,
                    new_title=new_title,
                    new_description=new_description,
                    selected_priority=new_priority
                )

        # 2. Validate the description only if a new description was submitted
        # An empty description means the existing description stays unchanged
        if new_description:
            result, message = valid_description(new_description)

            # If validation fails, return the edit form with an error
            if not result:
                connect.close()
                return render_template(
                    'edit.html',
                    task=task,
                    id=id,
                    priorities=priorities,
                    error=message,
                    new_title=new_title,
                    new_description=new_description,
                    selected_priority=new_priority
                )

        # 3. Validate the priority only if a new priority was selected
        # If no priority was selected, keep the existing priority
        if new_priority:
            result, message = valid_priority(new_priority)

            # If validation fails, return the edit form with an error
            if not result:
                connect.close()
                return render_template(
                    'edit.html',
                    task=task,
                    id=id,
                    priorities=priorities,
                    error=message,
                    new_title=new_title,
                    new_description=new_description,
                    selected_priority=new_priority
                )

        title = new_title if new_title else task['title']
        description = new_description if new_description else task['description']
        prioritiy = new_priority if new_priority else task['priority']

        # Update the task in the database:
        connect.execute("""
            UPDATE tasks
            SET title=?, description=?, priority=?
            WHERE id=?
        """, (title, description, prioritiy, id))
        # Save the changes:
        connect.commit()
        # Close the database connection:
        connect.close()
        
        # After processing the edit, redirect to the task list
        return redirect(url_for("view_tasks"))
    # For a GET request, display the edit form.
    connect.close()

    # For a GET request, find the task and display the edit form
    return render_template(
        'edit.html',
        id=id,
        task=task,
        priorities=priorities
    )


@app.route('/delete_tasks', methods=['POST'])
def delete_tasks():

    # Get the task ID from the submitted form
    task_id = request.form.get('id', type=int)

    # Reject a missing or invalid ID
    if task_id is None:
        abort(400)

    # Find and delete the matching task
    for task in tasks:
        if task['id'] == task_id:
            tasks.remove(task)
            break

    # Return to the task list
    return redirect(url_for('view_tasks'))



# Define the route for changing a task's status.
# Allow only POST requests because this route modifies a task.
@app.route('/check_tasks', methods=['POST'])
def status():

    # Get the task ID submitted through the form.
    # Convert the ID from a string to an integer.
    id = int(request.form.get('id'))

    # Loop through the tasks to find the one matching the submitted ID.
    for task in tasks:

        # Check whether the current task's ID matches the submitted ID.
        if task['id'] == id:

            # Check whether the task is currently completed.
            if task['status'] == "completed":

                # If completed, change its status back to pending.
                task.update({"status": 'pending'})

            else:

                # Otherwise, mark the task as completed.
                task.update({'status': "completed"})

    # Redirect the user to the task list after changing the status.
    return redirect(url_for('view_tasks'))



# Check whether this file is being run directly,
# rather than being imported as a module.
if __name__ == '__main__':

    # Start the Flask development server.
    # host='0.0.0.0' allows the server to accept connections
    # from other devices on the network, not just this computer.
    # port=5555 specifies the port on which the server listens.
    # debug=True enables debug mode, including automatic reloading
    # when code changes and detailed error pages during development.
    app.run(host='0.0.0.0', port=5555, debug=True)