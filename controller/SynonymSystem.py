from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from app.extensions import db, cache
from sqlalchemy import text
from models.TblDictionary import Dictionary
import functools


class SynonymSystem(Resource):

    def get(self, inword=None):
        
        engine = db.engine  # Get the engine used by db.Model
        print(engine.pool.status())  # Check connection pool usage

        response = {}
        if inword:
            cache_key = f"words_cache_{inword}"
        else:
            cache_key = "all"
        cached_data = cache.get(cache_key)  # Retrieve cached data
        '''
        cache.set("test_key", "Hello, Cache!", timeout=60)
        print(cache.get("test_key"))  # Should print "Hello, Cache!"
        '''

        if cached_data:  # If data is in cache, return it
            return jsonify({"data": cached_data, "cached": True})

        if inword:
            words = Dictionary.query.filter(Dictionary.word.like(f"%{inword}%")).all()
            response["cached"]= cache.get("words_cache") is not None
            if type(words) is list:
                print("its a list..")
                response['data'] = [word.to_dict() for word in words]
            else:
                print("not a list..")
                response['data'] = words.to_dict()
        else:
            try:
                words = Dictionary.query.all()
                response["cached"] = cache.get("words_cache") is not None
                response['data'] = [word.to_dict() for word in words]
            except Exception as e:
                print(f" Database connection failed: {e}")
        cache.set(cache_key, response, timeout=60)  # Store data in cache
        return jsonify(response)

    def post(self):
        
        data = request.json
        print("received data is ", data)
        word = data.get("word", None)
        synonym = data.get("synonym", None)

        if word and synonym:
            new_entry = Dictionary( word=word, synonym=synonym)  # Create new object
            db.session.add(new_entry)  # Add to session
            db.session.commit()
            return jsonify({"result": f"{word}:{synonym} added successfully"})
        else:
            return jsonify({"error": "data is incomplete .. word or synonym not resent"})

    def put(self, inword):
        
        data = request.json  # Get JSON data from request
        old_value = data.get("old_synonym")
        new_value = data.get("new_synonym")
        word = Dictionary.query.filter(
            (Dictionary.word.like(f"%{inword}%")) & (Dictionary.synonym.like(f"%{old_value}%"))).first()

        if word:
            word.synonym = new_value
            db.session.commit()
            return jsonify({"message": f"{inword} is updated with  value {new_value}"})
        else:
            return jsonify({"message": f"Combination {inword} and value {old_value} not found"})

    def delete(self, inword=None):
        
        if inword:
            words = Dictionary.query.filter(Dictionary.word.like(f"%{inword}%"))  # Fetch entry by ID
            print(jsonify([word.to_dict() for word in words]))
        else:
            print("Deleting all records..")
            db.session.query(Dictionary).delete()
            db.session.commit()
            return jsonify({"message": "Deleted All records"})

        if not words:  # Check if entry exists
            return jsonify({"error": "words not found"}), 404

        db.session.query(Dictionary).filter(Dictionary.word.like(f"%{inword}%")).delete(synchronize_session=False)
        db.session.commit()

        return jsonify({"message": f"Entries for all {inword} deleted successfully"})


