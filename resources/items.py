from flask_smorest import Blueprint, abort 
from flask import request, jsonify 
from schemas import ItemSchema, ItemUpdateSchema
from flask.views import MethodView 
from models import ItemModel 
from sqlalchemy.exc import SQLAlchemyError
from db import db 
from flask_jwt_extended import jwt_required, get_jwt

# Blueprint definition
blp=Blueprint("items", __name__, description="operations on stores")

# Route
@blp.route("/item/<int:item_id>")
class Items(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema)
    def get(self, item_id): 
        """ Retrieve a single item by ID"""
        item=ItemModel.query.get_or_404(item_id, description="ITem not found")
        return item  
    
    @jwt_required()
    def delete(self, item_id):
        """ Delete item by ID"""
        jwt=get_jwt()
        if   jwt.get("is_admin"):
            abort(401, message="Admin privilege required")
        item=ItemModel.query.get_or_404(item_id, description="Item not found")
        try:
            db.session.delete(item)
            db.session.commit()
        except SQLAlchemyError :
            abort(500, message="An error occurred while deleting the item")
        return jsonify({"message":"Item deleted successfully"}), 200
    
    @jwt_required()
    @blp.arguments(ItemUpdateSchema)
    @blp.response(200, ItemUpdateSchema)
    def put(self, item_data, item_id):
     # Updating existing item. If the item doesn't exist, create it.
     
        item=ItemModel.query.get(item_id)
        if item:
            # update existing item 
            for key, value in item_data.items():
                setattr(item, key, value)
            else:
            # Create a new item if it doesn't exist. 
                item_data["id"]=item_id
                item=ItemModel(**item_data)
                
            try:
                db.session.merge(item)
                db.session.commit()
            except SQLAlchemyError:
                abort(500, message="An error occurred while updating item")
                
            return item 
        
@blp.route("/item")
class ItemList(MethodView):
    @jwt_required()
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        """ Retrieve a list of all items  """
        items=ItemModel.query.all()
        return  items 
    
    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        try:
            item=ItemModel(**item_data)
        except TypeError as e:
            abort(400, message="Invalid data format")
        
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError  as e:
            abort(500, message=f"An error occurred while inserting data {str(e)} ",), 
        
        return item