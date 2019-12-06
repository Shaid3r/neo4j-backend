import json
from uuid import uuid4

import falcon


class DishResource:
    def __init__(self, session):
        self.session = session

    def on_get_collection(self, req, resp):
        query_result = self.session.run("MATCH (d:Dish) RETURN d")

        result = []
        for record in query_result:
            result.append({
                'name': record['d']['name'],
                'uuid': record['d']['uuid']
            })

        resp.body = json.dumps(result)

    def on_post_collection(self, req, resp):
        name = req.media['name']
        dish_uuid = str(uuid4())
        dish_node_id = self.session.run("CREATE (d:Dish { uuid: {uuid}, name: {name} }) RETURN id(d)",
                                        name=name, uuid=dish_uuid).single().value()

        for ingredient in req.media['ingredients']:
            self.session.run("""
                MATCH (d:Dish) WHERE id(d) = {dish_id}
                MERGE (i:Ingredient { name: {name} }) 
                CREATE (d)-[:CONSISTS { quantity: {quantity} }]->(i)
                """, dish_id=dish_node_id, name=ingredient['name'], quantity=ingredient['quantity'])

        resp.status = falcon.HTTP_201
        resp.body = json.dumps({'dish_uuid': dish_uuid})

    def on_get(self, req, resp, dish_uuid):
        query_result = self.session.run("""
            MATCH (d:Dish { uuid: {uuid} })
            MATCH (d)-[r:CONSISTS]->(i:Ingredient)
            RETURN d.name, i, r
            """, uuid=dish_uuid)

        if query_result.peek() is None:
            resp.status = falcon.HTTP_404
            return

        result = {
            'name': query_result.peek()['d.name'],
            'ingredients': []
        }

        for record in query_result:
            result['ingredients'].append({
                'name': record['i']['name'],
                'quantity': record['r']['quantity']
            })

        resp.body = json.dumps(result)

    def on_put(self, req, resp, dish_uuid):
        query_result = self.session.run("""
            MATCH (d:Dish { uuid: {uuid} })
            SET d.name = {new_name}
            """, uuid=dish_uuid, new_name=req.media['name'])

        if query_result.summary().counters.properties_set == 0:
            resp.status = falcon.HTTP_404
            return

        resp.status = falcon.HTTP_201

    def on_delete(self, req, resp, dish_uuid):
        query_result = self.session.run("""
            MATCH(d: Dish { uuid: {uuid} })
            DETACH DELETE d
            """, uuid=dish_uuid)

        if query_result.summary().counters.nodes_deleted == 0:
            resp.status = falcon.HTTP_404
            return

        resp.status = falcon.HTTP_201

    def on_post_recommendation(self, req, resp):
        ingredient_list = req.media['ingredients']

        query_result = self.session.run("""
            MATCH (i:Ingredient)
            WHERE i.name IN {ingredient_list}
            MATCH (d:Dish)-[r:CONSISTS]->(i)
            RETURN d, count(r) as similarity
            ORDER BY similarity DESC
            """, ingredient_list=ingredient_list)

        result = []
        for record in query_result:
            result.append({
                'dish_name': record['d']['name'],
                'dish_uuid': record['d']['uuid'],
                'similarity': record['similarity']
            })

        resp.body = json.dumps(result)
