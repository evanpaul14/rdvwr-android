import os

os.environ.setdefault("REDDIT_OAUTH", "1")

import app as flaskapp


def start(port=8002):
    update_dir = os.environ.get("RDVWR_UPDATE_DIR", "")
    if update_dir:
        static_dir = os.path.join(update_dir, "static")
        if os.path.isdir(static_dir):
            flaskapp.app.static_folder = os.path.abspath(static_dir)
    flaskapp.app.run(host="127.0.0.1", port=port, threaded=True,
                     use_reloader=False, debug=False)
