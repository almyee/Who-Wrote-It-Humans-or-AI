from flask import Flask, request, render_template_string

# Initialize Flask app
app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return render_template_string('<h1>Welcome to the Flask App</h1><p><a href="/input">Go to Input Form</a></p>')

# Input form route
@app.route('/input', methods=['GET', 'POST'])
def input_form():
    if request.method == 'POST':
        user_input = request.form['user_input']
        return f'<h1>You entered: {user_input}</h1>'
    return '''<form method="post">
                  <input type="text" name="user_input" placeholder="Enter something">
                  <button type="submit">Submit</button>
              </form>'''

# Run the app
if __name__ == '__main__':
    app.run(debug=True)

