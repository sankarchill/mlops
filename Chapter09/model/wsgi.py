# This is just a simple wrapper for gunicorn to find your app.
# If you want to change the algorithm file, simply change "predictor" above to the
# new file.

import app as myapp
app = myapp.app