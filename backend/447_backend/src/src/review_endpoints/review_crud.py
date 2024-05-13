import sys
from pathlib import Path

LIBAPI_FP = str(Path(__file__).parent.parent.parent.parent.parent)
sys.path.append(LIBAPI_FP)
sys.path.append(Path(__file__).parent)

from flask import Blueprint, request, Response, make_response, jsonify
from database import MySQL_Database
from utils import escape_single_quotes

blueprint = Blueprint("review", __name__)
database = None
review_table = None

def review_init_db(mysql_host, mysql_user, mysql_password, mysql_database):
    global database, review_table

    database = MySQL_Database(
        host = mysql_host,
        user = mysql_user,
        password = mysql_password
    )

    if not database.use(mysql_database):
        raise RuntimeError(f"Could not find database {mysql_database}")
    
    review_table = database.get_table("review")

    if review_table == None:
        raise RuntimeError(f"Could not find review table in database")
    

def create_review(json) -> Response:
    account_id = json["account_id"]
    music_id = json["music_id"]
    review = escape_single_quotes(json["review"])

    columns = ["`account_id`", "`music_id`", "`review`"]
    values = [account_id, music_id, f"\'{review}\'"]
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
        results.append({
            "review_id" : review_id,
            "account_id" : account_id,
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


def delete_review(json) -> Response:
    review_id = json["review_id"]

    review_table.delete("`review_id`", review_id)

    response = make_response(jsonify({"success":""}), 200)
    response.headers["Content-Type"] = "application/json"

    return response


@blueprint.route("/create_review", methods=["POST"])
def app_create_review() -> Response:
    if request.method == "POST":
        return create_review(request.get_json)
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"

    return response


@blueprint.route("/get_reviews", methods=["POST"])
def app_get_reviews() -> Response:
    if request.method == "POST":
        return get_reviews(request.get_json)
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"

    return response


@blueprint.route("/delete_review", methods=["POST"])
def app_delete_review() -> Response:
    if request.method == "POST":
        return delete_review(request.get_json)
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"

    return response