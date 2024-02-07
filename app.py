# Import necessary modules
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request
from crawler import gather_and_store, search_publications

# Create a Flask application instance
app = Flask(__name__)

# Create an instance of scheduler
scheduler = BackgroundScheduler()

# Add a job to the scheduler to run gather_and_store function every week
scheduler.add_job(gather_and_store, 'interval', weeks=1)

# Start the scheduler
scheduler.start()

# Define the index route
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # If the request method is POST, call gather_and_store function and render the results template
        results = gather_and_store()
        return render_template('results.html', results=results)
    # If the request method is GET, render the index template
    return render_template('index.html')

# Define the search route
@app.route('/search', methods=['GET'])
def search_query():
    # Get the query parameter from the request
    query = request.args.get('query')
    # Call search_publications function with the query and get the results
    results = search_publications(query)
    # Render the results template with the results
    return render_template('results.html', results=results)

# Run the Flask application if this file is executed directly
if __name__ == '__main__':
    app.run(debug=True)