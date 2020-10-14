from threading import Thread
import time
import sqlite3
import os
from typing import Dict, List, Tuple, Union

from flask import g, Flask, render_template
import numpy as np

app = Flask("stockhorn")

COSTS = [0]

PATH_DB = 'db.db'


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(PATH_DB)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


class ThreadUpdate(Thread):
    def __init__(self, season: str, last=0):
        self.updated = last
        self.sname: str = season
        super().__init__(name="thread-update")

    def run(self) -> None:
        global COSTS
        while True:
            time.sleep(10)
            t = COSTS[-1] + np.random.normal(0, 5)
            with open(f'seasons/{self.sname}', 'a', encoding='utf-8') as f:
                f.write(str(t) + '\n')
            COSTS.append(t)
            self.updated += 1


@app.route("/public/cost/all/")
def public_cost_all():
    return {"cost": COSTS, "updated": _ut.updated}, 200


@app.route("/public/cost/all/chart/")
def public_cost_all_chart():
    return {"cost": [{"x": i, "y": v} for i, v in enumerate(COSTS)], "updated": _ut.updated}, 200


@app.route("/public/cost/now/")
def public_cost_now():
    return {"cost_now": COSTS[-1], "updated": _ut.updated}, 200


@app.route("/public/cost/period/<int:start>/<int:end>/")
def public_cost_period(start: int, end: int):
    if start <= end < len(COSTS):
        return {"cost": COSTS[start:end + 1], "updated": _ut.updated}, 200
    else:
        return {"cost": [], "updated": _ut.updated}, 200


@app.route("/")
@app.route("/front/")
def public_front():
    return render_template('front.html')


if __name__ == '__main__':
    season_name = 'vc-rrt'
    if os.path.exists(rf"seasons/{season_name}"):
        COSTS += [float(line) for line in open(rf"seasons/{season_name}", 'r', encoding='utf-8')]
        _ut = ThreadUpdate(season_name, len(COSTS) - 1)
    else:
        _ut = ThreadUpdate(season_name)
    _ut.start()
    app.run('192.168.0.4', port=54321)
