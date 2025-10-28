
from flask import Flask, render_template, request, url_for

app = Flask(__name__)

# Home page route
@app.route('/')
def home():
    return render_template('index.html')

# Contact form route
@app.route('/contact', methods=['POST'])
def contact():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    # Save message to a file
    with open('messages.txt', 'a') as f:
        f.write(f"Name: {name}\nEmail: {email}\nMessage: {message}\n---\n")

    # Show thank-you message
    return render_template('index.html', message_sent=True)

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, render_template, request, url_for

app = Flask(__name__)

# Home page route
@app.route('/')
def home():
    return render_template('index.html')

# Contact form route
@app.route('/contact', methods=['POST'])
def contact():
    name = request.form['name']
    email = request.form['email']
    message = request.form['message']

    # Save message to a file
    with open('messages.txt', 'a') as f:
        f.write(f"Name: {name}\nEmail: {email}\nMessage: {message}\n---\n")

    # Show thank-you message
    return render_template('index.html', message_sent=True)

if __name__ == '__main__':
    app.run(debug=True)
