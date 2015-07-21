#!flask/bin/python
from my_trio import app

app.run(debug=True, port=5000)