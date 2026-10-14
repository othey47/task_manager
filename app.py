# Import the tools we need from Flask
from flask import Flask, render_template, redirect, url_for, request, abort

# Create the Flask application
app = Flask(__name__)

# Create an empty list to store tasks
tasks = []

# Define the available priority levels for tasks
priorities = ['Low', 'Medium', 'High']

# Generate an ID for a new task
def get_id(tasks):
    # Return the number of tasks plus 1
    # Example: if there are 3 tasks, the new ID will be 4
    return int(len(tasks)+1)

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

# Define the route for displaying all tasks
@app.route('/view_tasks')
def view_tasks():
    
    # Render view.html and pass the tasks list to the template
    # The template can use Jinja to loop through and display each task
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

        # All validation checks passed, so generate a new task ID
        id = get_id(tasks)        

        # Create a new task dictionary and add it to the tasks list
        # Every new task starts with the status "pending"
        tasks.append({
            "id" : id,
            "title" : title,
            "description" : description,
            "priority" : priority,
            "status" : "pending"
        })

        # Redirect the user to the page displaying all tasks
        return redirect(url_for('view_tasks'))    
    
    # If the request is GET, display the empty Add Task form
    return render_template('add.html', priorities=priorities)


# Define the route for editing a task.
# Allow GET requests to display the form and POST requests to submit changes.
@app.route('/edit_tasks', methods=['GET', 'POST'])
def edit_tasks():

    # Get the task ID from the URL query parameter
    id = int(request.args.get('id'))

    # Print debugging information to help inspect the request and task list
    print("ID:", id)
    print("TASKS:", tasks)

    # Check whether the user submitted the edit form
    if request.method == 'POST':

        # Find the task that matches the ID from the URL
        for task in tasks:
            if task['id'] == id:

                # Get the submitted values from the form
                # strip() removes whitespace around the title and description
                new_title = request.form.get('title', '').strip()
                new_description = request.form.get('description', '').strip()
                new_priority = request.form.get('priority')

                # 1. Validate the title only if a new title was submitted
                # An empty title means the existing title should remain unchanged
                if new_title:
                    result, message = valid_title(new_title)

                    # If validation fails, return the edit form with an error
                    # and preserve the user's submitted values
                    if not result:
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

                # 2. Validate the description only if a new description was submitted
                # An empty description means the existing description stays unchanged
                if new_description:
                    result, message = valid_description(new_description)

                    # If validation fails, return the edit form with an error
                    if not result:
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

                # All submitted values passed validation.
                # Update only the fields that contain new values.
                if new_title:
                    task['title'] = new_title

                if new_description:
                    task['description'] = new_description

                if new_priority:
                    task['priority'] = new_priority

        # After processing the edit, redirect to the task list
        return redirect(url_for("view_tasks"))

    # For a GET request, find the task and display the edit form
    for task in tasks:
        if task['id'] == id:
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