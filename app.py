from flask import Flask, jsonify
from flask_restx import Api, Resource, fields

app = Flask(__name__)
api = Api(app, version='1.0', title='API REST Documentation',
          description='Une API REST simple avec Swagger et Flask-RESTX.')

# Modèle d'objet pour Swagger
ns = api.namespace('object', description='Opérations liées aux objets')

object_model = api.model('Object', {
    'id': fields.Integer(required=True, description='ID unique'),
    'name': fields.String(required=True, description='Nom de l\'objet'),
    'description': fields.String(description='Description de l\'objet')
})

# Données en mémoire pour simuler une base de données
OBJECTS = []

# Classe pour gérer les actions sur la collection d'objets
@ns.route('/')
class ObjectList(Resource):
    @ns.doc('list_objects')
    def get(self):
        """Retourner la liste de tous les objets"""
        return OBJECTS, 200

    @ns.doc('create_object')
    @ns.expect(object_model)
    def post(self):
        """Créer un nouvel objet"""
        new_object = api.payload
        OBJECTS.append(new_object)
        return new_object, 201

# Classe pour gérer les actions sur un objet spécifique
@ns.route('/<int:id>')
@ns.response(404, 'Object not found')
@ns.param('id', 'L\'ID de l\'objet')
class Object(Resource):
    @ns.doc('get_object')
    def get(self, id):
        """Retourner un objet spécifique par son ID"""
        for obj in OBJECTS:
            if obj['id'] == id:
                return obj, 200
        return {"message": "Object not found"}, 404

    @ns.doc('update_object')
    @ns.expect(object_model)
    def put(self, id):
        """Mettre à jour complètement un objet"""
        for obj in OBJECTS:
            if obj['id'] == id:
                obj.update(api.payload)
                return obj, 200
        return {"message": "Object not found"}, 404

    @ns.doc('partial_update_object')
    def patch(self, id):
        """Mettre à jour partiellement un objet"""
        for obj in OBJECTS:
            if obj['id'] == id:
                for key, value in request.json.items():
                    obj[key] = value
                return obj, 200
        return {"message": "Object not found"}, 404

    @ns.doc('delete_object')
    def delete(self, id):
        """Supprimer un objet"""
        global OBJECTS
        OBJECTS = [obj for obj in OBJECTS if obj['id'] != id]
        return {"message": "Object deleted"}, 200


# Point d'entrée principal
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)