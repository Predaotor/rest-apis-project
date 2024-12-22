from flask.views import MethodView 
from flask import request, jsonify
from flask_smorest import Blueprint, abort 
from schemas import StoreSchema 
from models import StoreModel, ItemModel
from db import db
from sqlalchemy.exc import SQLAlchemyError
from flask_jwt_extended import jwt_required

blp=Blueprint("stores", __name__, description="Operations on Stores")

@blp.route("/store/<int:store_id>")
class Store(MethodView):
    @jwt_required()
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        """ Retrieve a single store """
        store=StoreModel.query.get_or_404(store_id, description="Store not found")
        return store  
    
    def delete(self, store_id):
        """ Delete a single Store """
        store=StoreModel.query.get_or_404(store_id, description="Store not found")
        try:
            db.session.delete(store)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred during the deleting store")
        return jsonify({"message":"Store deleted successfully "})
    
    
@blp.route("/store")
class StoreList(MethodView):
    @jwt_required()
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        # Get all of the stores 
        stores=StoreModel.query.all()
        return stores 
    
    @jwt_required()
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        store=StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the data in the database")
        return store 