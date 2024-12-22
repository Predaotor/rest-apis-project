from flask.views import MethodView 
from flask import request, jsonify
from flask_smorest import Blueprint, abort 
from schemas import TagSchema, TagAndItemSchema
from models import TagModel, StoreModel, ItemModel
from db import db
from sqlalchemy.exc import SQLAlchemyError 
from flask_jwt_extended import jwt_required

blp=Blueprint("tags", __name__, description="operations on tags")

@blp.route("/store/<int:store_id>/tag")
class TagsInStore(MethodView):
    @jwt_required()
    @blp.response(200, TagSchema)
    def get(self, store_id):
        store=StoreModel.query.get_or_404(store_id) 
        return store.tags.all()
    
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        if TagModel.query.filter(TagModel.store_id, TagModel.name==tag_data["name"]).first():
            abort(400, message="A tag with that name already exists in that store")
        tag=TagModel(**tag_data, store_id=store_id)
        
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return tag 
    
@blp.route("/item/<int:item_id>/tag/<int:tag_id>")
class LinkTagsInItem(MethodView):
    @jwt_required()
    @blp.response(201, TagSchema)
    def post(self, item_id,tag_id):
        item=ItemModel.query.get_or_404(item_id)
        tag=TagModel.query.get_or_404(tag_id)
        
        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return tag
    
    @jwt_required()
    @blp.response(201, TagSchema)
    def delete(self, item_id,tag_id):
        item=ItemModel.query.get_or_404(item_id)
        tag=TagModel.query.get_or_404(tag_id)
        
        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return {"message":"Item removed from tag", "item":item, "tag":tag}
    
    
    
    
@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @jwt_required()
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag=TagModel.query.get_or_404(tag_id)
        
        return tag
    
    @jwt_required()
    @blp.response(202, 
                  description="Deletes a tag if no item is tagged with it",
                  example={"message":"Tag deleted"})
    @blp.alt_response(404, description="Tag not Found")
    @blp.alt_response(400, description="Returned if the tag is assigned to one or more items.")
    def delete(self, tag_id):
        tag=TagModel.query.get_or_404(tag_id)
        
        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message":"Tag deleted"}
        abort(400, message="Couldn't delete the tag make sure the tag is not associated with any item.")