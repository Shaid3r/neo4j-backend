import json


class IngredientResource:
    def __init__(self, session):
        self.session = session

    def on_get_collection(self, req, resp):
        query_result = self.session.run("MATCH (i:Ingredient) RETURN i")

        result = []
        for record in query_result:
            result.append(record['i']['name'])

        resp.body = json.dumps(result)

    def on_get_most_used(self, req, resp):
        query_result = self.session.run("""
            MATCH (:Dish)-[r:CONSISTS]->(i:Ingredient)
            RETURN i.name, count(r) as popularity
            ORDER BY popularity DESC
            """)

        result = []
        for record in query_result:
            result.append({
                'ingredient_name': record['i.name'],
                'popularity': record['popularity'],
            })

        resp.body = json.dumps(result)
