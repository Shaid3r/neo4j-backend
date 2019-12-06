import os

from neo4j.v1 import GraphDatabase, basic_auth


class Database:
    def __init__(self):
        graphenedb_url = os.environ.get("GRAPHENEDB_BOLT_URL")
        graphenedb_user = os.environ.get("GRAPHENEDB_BOLT_USER")
        graphenedb_pass = os.environ.get("GRAPHENEDB_BOLT_PASSWORD")

        if None in [graphenedb_url, graphenedb_user, graphenedb_pass]:
            print("GRAPHENEDB_BOLT_URL, GRAPHENEDB_BOLT_USER, GRAPHENEDB_BOLT_PASSWORD should be set")
            exit(1)

        print("Connecting to {} as {}".format(graphenedb_url, graphenedb_user))

        try:
            self.driver = GraphDatabase.driver(graphenedb_url, auth=basic_auth(graphenedb_user, graphenedb_pass))
            self.session = self.driver.session()
        except Exception as e:
            raise e

    def __del__(self):
        try:
            self.session.close()
            print("Database connection closed")
        except AttributeError:
            pass
