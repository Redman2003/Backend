import sys
from pathlib import Path

LIBAPI_FP = str(Path(__file__).parent.parent.parent.parent.parent)
sys.path.append(LIBAPI_FP)
sys.path.append(Path(__file__).parent)

from flask import Blueprint, request, Response, make_response, jsonify
from database import MySQL_Database
from utils import escape_single_quotes

blueprint = Blueprint("review_comment", __name__)
database = None
review_comment_table = None

def review_comment_init_db(mysql_host, mysql_user, mysql_password, mysql_database):
    global database, review_comment_table

    database = MySQL_Database(
        host = mysql_host,
        user = mysql_user,
        password = mysql_password
    )

    if not database.use(mysql_database):
        raise RuntimeError(f"Could not find database {mysql_database}")
    
    review_comment_table = database.get_table("review")

    if review_comment_table == None:
        raise RuntimeError(f"Could not find review_comment table in database")
    

def create_review_comment(json) -> Response:
    review_id = json["review_id"]
    account_id = json["account_id"]
    comment = escape_single_quotes(json["comment"])

    columns = ["`review_id`", "`account_id`", "`comment`"]
    values = [review_id, account_id, f"\'{comment}\'"]
    review_comment_table.insert(columns, values)

    response = make_response(jsonify({"success":""}), 200)
    response.headers["Content-Type"] = "application/json"

    return response


def get_review_comments(json) -> Response:
    method = json["method"]

    comments = []

    if method == "review":
        comments = review_comment_table.get_all("`review_id`", json["review_id"])
    elif method == "account":
        comments = review_comment_table.get_all("`account_id`", json["account_id"])
    else:
        response = make_response(
            jsonify({"error":"get method for review is invalid"}),
            405
        )
        response.headers["Content-Type"] = "application/json"
        return response
    
    results = []
    
    for comment in comments:
        (review_comment_id, review_id, account_id, comment, like_count, dislike_count, creation_date) = comment
        results.append({
            "review_comment_id" : review_comment_id,
            "review_id" : review_id,
            "account_id" : account_id,
            "comment" : comment,
            "like_count" : like_count,
            "dislike_count" : dislike_count,
            "creation_date" : creation_date,
        })

    response = make_response(
        jsonify({"result":results}),
        200
    )
    response.headers["Content-Type"] = "application/json"

    return response


def delete_review_comment(json) -> Response:
    review_comment_id = json["review_comment_id"]

    review_comment_table.delete("`review_comment_id`", review_comment_id)

    response = make_response(jsonify({"success":""}), 200)
    response.headers["Content-Type"] = "application/json"

    return response


@blueprint.route("/create_review_comment", methods=["POST"])
def app_create_review_comment() -> Response:
    if request.method == "POST":
        return create_review_comment(request.get_json)
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"

    return response


@blueprint.route("/get_review_comments", methods=["POST"])
def app_get_review_comments() -> Response:
    if request.method == "POST":
        return get_review_comments(request.get_json)
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"

    return response


@blueprint.route("/delete_review_comment", methods=["POST"])
def app_delete_review_comment() -> Response:
    if request.method == "POST":
        return delete_review_comment(request.get_json)
    
    response = make_response(
        jsonify({"error":"only post method is allowed"}),
        405
    )
    response.headers["Content-Type"] = "application/json"

    return response