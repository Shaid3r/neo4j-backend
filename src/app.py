import falcon

from db import Database
from resources import DishResource, IngredientResource

db = Database()

# Create resources
dish_resource = DishResource(db.session)
ingredient_resource = IngredientResource(db.session)

application = falcon.API()

# Add routes
application.add_route('/dishes', dish_resource, suffix='collection')
application.add_route('/dishes/recommendation', dish_resource, suffix='recommendation')
application.add_route('/dish/{dish_uuid}', dish_resource)
application.add_route('/ingredients', ingredient_resource, suffix='collection')
application.add_route('/ingredients/most_used', ingredient_resource, suffix='most_used')

if __name__ == '__main__':
    from wsgiref import simple_server  # NOQA

    httpd = simple_server.make_server('127.0.0.1', 8000, application)
    print("Listening on localhost:8000")
    httpd.serve_forever()
