import datetime
import json

from bl import ManagerImpl
from domain.base import DomainBase
from domain.exceptions import ServiceException
from domain.player import Player
from domain.match import Match
from da import DaoImpl
from firebase_client import FirebaseClientImpl


def handle(event, _):
    return Handler.get_instance().handle(event)


class Handler:
    instance = None

    @staticmethod
    def get_instance():
        if Handler.instance is None:
            Handler.instance = Handler(ManagerImpl(FirebaseClientImpl(), DaoImpl()))
        return Handler.instance

    def __init__(self, manager):
        self.manager = manager

    def handle(self, event):
        try:
            if event is None or "resource" not in event or "httpMethod" not in event:
                raise ServiceException("Invalid request. No 'resource', or 'httpMethod' found in the event", 400)

            resource, method = event["resource"], event["httpMethod"]  # These will be used to specify which endpoint was being hit
            print(f"Received a {method} on {resource}")
            path_params = event.get("pathParameters", {}) if event.get("pathParameters") is not None else {}  # This will be used to get IDs and other parameters from the URL
            query_params = event.get("queryStringParameters", {}) if event.get("queryStringParameters") is not None else {}  # This will be used to get IDs and other parameters from the URL
            try:
                body = json.loads(event["body"])  # This will be used for most POSTs and PUTs
            except (TypeError, KeyError, ValueError):
                body = None

            self.manager.validate_token(self.get_token(event))

            if resource == "/users" and method == "POST":
                response_body = self.manager.user
            elif resource == "/players" and method == "GET":
                response_body = self.manager.get_players()
            elif resource == "/players" and method == "POST":
                response_body = self.manager.create_player(Player.from_dict(body, self.manager.user))
            elif resource == "/players/{id}" and method == "PUT":
                response_body = self.manager.update_player(path_params["id"], Player.from_dict(body, self.manager.user))
            elif resource == "/players/{id}" and method == "DELETE":
                response_body = self.manager.delete_player(path_params["id"])
            elif resource == "/matches" and method == "GET":
                response_body = self.manager.get_matches()
            elif resource == "/matches" and method == "POST":
                response_body = self.manager.create_match(Match.from_dict(body, self.manager.user))
            elif resource == "/matches/{id}" and method == "DELETE":
                response_body = self.manager.delete_match(path_params["id"])
            else:
                raise ServiceException("Invalid path: '{} {}'".format(resource, method))

            print("Responding with", response_body)
            return format_response(response_body)
        except ServiceException as e:
            return format_response({"error": e.error_message}, e.status_code)

    @staticmethod
    def get_token(event):
        # Lower case all the keys, then look for token
        return {k.lower(): v for k, v in event["headers"].items()}.get("x-firebase-token")


def format_response(body=None, status_code=200):
    return {
        "statusCode": status_code,
        "body": json.dumps(body, default=default_serialize) if body is not None else None
    }


def default_serialize(x):
    if isinstance(x, datetime.datetime):
        return x.strftime("%Y-%m-%dT%H:%M:%SZ")
    elif isinstance(x, DomainBase):
        return x.to_dict()
    else:
        return x.__dict__
