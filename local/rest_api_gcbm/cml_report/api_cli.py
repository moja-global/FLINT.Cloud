import os
import sys
sys.path.append('../')
import app

class API_CLI:
    app = app()
    def new_simulation():
        return app.gcbm_new()


cli = API_CLI()
res = cli.new_simulation()
print(res)
