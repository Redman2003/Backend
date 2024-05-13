import sys
from pathlib import Path

LIBAPI_FP = str(Path(__file__).parent.parent.parent.parent.parent)
sys.path.append(LIBAPI_FP)
sys.path.append(Path(__file__).parent)

from flask import Blueprint, request, Response, make_response, jsonify
from database import MySQL_Database
from utils import escape_single_quotes
from datetime import date

blueprint = Blueprint("review", __name__, url_prefix="/review")
database = None
review_table = None
acct_table = None

def review_init_db(mysql_host, mysql_user, mysql_password, mysql_database):
    global database, review_table, acct_table

    database = MySQL_Database(
        host = mysql_host,
        user = mysql_user,
        password = mysql_password
    )

    if not database.use(mysql_database):
        raise RuntimeError(f"Could not find database {mysql_database}")
    
    review_table = database.get_table("review")
    acct_table = database.get_table("acct")

    if review_table == None:
        raise RuntimeError(f"Could not find review table in database")
    

def create_review(json) -> Response:
    account_id = json["account_id"]
    music_id = json["music_id"]
    review = escape_single_quotes(json["review"])

    columns = ["`account_id`", "`music_id`", "`like_count`", "`dislike_count`", "`creation_date`", "`review`"]
    values = [account_id, music_id, 0, 0, "\'2024-5-6\'", f"\'{review}\'"]
    review_table.insert(columns, values)

    response = make_response(jsonify({"success":""}), 200)
    response.headers["Content-Type"] = "application/json"


    return response


def get_reviews(json) -> Response:
    method = json["method"]

    reviews = []

    if method == "account":
        reviews = review_table.get_all("`account_id`", json["account_id"])
    elif method == "music":
        reviews = review_table.get_all("`music_id`", json["music_id"])
    else:
        response = make_response(
            jsonify({"error":"get method for review is invalid"}),
            405
        )
        response.headers["Content-Type"] = "application/json"
        return response
    
    results = []
    
    for review in reviews:
        (review_id, account_id, music_id, like_count, dislike_count, creation_date, review_text) = review

        (account_username,) = acct_table.get("`username`", "`account_id`", account_id)[0]

        results.append({
            "review_id" : review_id,
            "account_id" : account_id,
            "account_username" : account_username,
            "music_id" : music_id,
            "like_count" : like_count,
            "dislike_count" : dislike_count,
            "creation_date" : creation_date,
            "review" : review_text
        })

    response = make_response(
        jsonify({"result":results}),
        200
    )
    response.headers["Content-Type"] = "application/json"

    return response

def get_reviews_by_name(json) -> Response:
    query = json["query"]

    review_ids = []

    music_ids = []


    music_covers = []
    album_ids = []
    single_ids = []


    CMD = f'SELECT album_id, album_cover FROM album WHERE album_name = \'{query}\''
    database.execute(CMD)
    response = database.fetchall()

    for index in response:
        music_covers.append(index[1])
        album_ids.append(index[0])

    for album_id in album_ids:
        CMD = f'SELECT music_id FROM music WHERE album_id = {album_id}'
        database.execute(CMD)
        response = database.fetchall()
      

        for index in response:
            music_ids.append(index[0])


    CMD = f'SELECT single_id, single_cover FROM single WHERE single_name = \'{query}\''
    database.execute(CMD)
    response = database.fetchall()

    for index in response:
        music_covers.append(index[1])
        single_ids.append(index[0])

    for single_id in single_ids:
        CMD = f'SELECT music_id FROM music WHERE single_id = {single_id}'
        database.execute(CMD)
        response = database.fetchall()
      

        for index in response:
            music_ids.append(index[0])

    for music_id in music_ids:
        CMD = f'SELECT review_id FROM review WHERE music_id = {music_id}'
        database.execute(CMD)
        response = database.fetchall()

        for index in response:
            review_ids.append(index[0])

    resp = []

    for i in range(len(review_ids)):
        data = {
            'review_id':review_ids[i],
            'image':music_covers[i]
        }
        resp.append(data)

    response = make_response(
        jsonify({"result":resp}),
        200
    )


    return response


def delete_review(json) -> Response:
    review_id = json["review_id"]

    review_table.delete("`review_id`", review_id)

    response = make_response(jsonify({"success":""}), 200)
    response.headers["Content-Type"] = "application/json"

    return response


@blueprint.route("/create_review", methods=["POST"])
def app_create_review() -> Response:
    if request.method == "POST":
        return create_review(request.get_json())
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"

    return response


@blueprint.route("/get_reviews", methods=["POST"])
def app_get_reviews() -> Response:
    if request.method == "POST":
        return get_reviews(request.get_json())
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"

    return response


@blueprint.route("/delete_review", methods=["POST"])
def app_delete_review() -> Response:
    if request.method == "POST":
        return delete_review(request.get_json())
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"

    return response