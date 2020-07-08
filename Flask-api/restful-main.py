############################
# Contain all endpoints and logic
############################

from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
from model import db, product_schema, products_schema, Product, app

api = Api(app)

# Every Class is an Endpoint

class add_product(Resource):

    def post(self):
        self.name = request.json['name']
        self.description = request.json['description']
        self.price = request.json['price']
        self.qty = request.json['qty']
        self.new_product = Product(self.name, self.description, self.price, self.qty)
        db.session.add(self.new_product)
        db.session.commit()
        return product_schema.jsonify(self.new_product)


class get_all_products(Resource):

    def get(self):
        self.all_products = Product.query.all()
        result = products_schema.dump(self.all_products)
        return jsonify(result)


class get_product(Resource):

    def get(self, id):
        self.product = Product.query.get(id)
        result = product_schema.dump(self.product)
        return jsonify(result)


class update_product(Resource):

    def put(self, id):
        self.update_product = Product.query.get(id)

        self.name = request.json['name']
        self.description = request.json['description']
        self.price = request.json['price']
        self.qty = request.json['qty']

        self.update_product.name = self.name
        self.update_product.description = self.description
        self.update_product.price = self.price
        self.update_product.qty = self.qty

        db.session.commit()

        return product_schema.jsonify(self.update_product)


class delete_product(Resource):

    def delete(self, id):
        product = Product.query.get(id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({"deleted": "product"})


class home(Resource):
    def get(self):
        return jsonify({"HI": "Welcome"})

# Routes
api.add_resource(home, '/')
api.add_resource(add_product, '/product')
api.add_resource(get_all_products, '/products')
api.add_resource(get_product, '/product/<id>')
api.add_resource(update_product, '/product/<id>')
api.add_resource(delete_product, '/product/<id>')

if __name__ == '__main__':
    app.run(debug=True)
