from flask import Flask, render_template,url_for

app = Flask(__name__)

@app.route('/')
def main():
    total = 0
    pending = 0
    completed = 0
    return render_template("index.html", total=total, pending=pending, completed=completed)







if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)