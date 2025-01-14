from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship

app = Flask(__name__)
api = Api(app, version='1.0', title='Champomix API',
          description='API REST pour la gestion de la base Champomix')

# Configuration de la base de données
DATABASE_URL = "postgresql://postgres:root@localhost:5432/API-Champomix"
engine = create_engine(DATABASE_URL)
Session = scoped_session(sessionmaker(bind=engine))
session = Session()
Base = declarative_base()

# Modèles ORM
class Champomi(Base):
    __tablename__ = 'champomi'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(Text)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    pseudo = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship("User", backref="orders")

class OrderChampomi(Base):
    __tablename__ = 'order_champomi'
    order_id = Column(Integer, ForeignKey('orders.id'), primary_key=True)
    champomi_id = Column(Integer, ForeignKey('champomi.id'), primary_key=True)

# Création des tables
Base.metadata.create_all(bind=engine)

# Modèle pour Swagger
champomi_model = api.model('Champomi', {
    'id': fields.Integer(readOnly=True, description='ID unique du produit'),
    'name': fields.String(required=True, description='Nom du produit'),
    'price': fields.Float(required=True, description='Prix du produit'),
    'description': fields.String(description='Description du produit')
})

# Namespace pour Champomi
ns_champomi = api.namespace('champomi', description='Opérations sur les produits Champomi')

@ns_champomi.route('/')
class ChampomiList(Resource):
    @ns_champomi.doc('list_champomi')
    def get(self):
        """Retourner la liste de tous les produits"""
        champomis = session.query(Champomi).all()
        return [
            {
                'id': c.id,
                'name': c.name,
                'price': float(c.price),
                'description': c.description
            } for c in champomis
        ], 200

    @ns_champomi.doc('create_champomi')
    @ns_champomi.expect(champomi_model)
    def post(self):
        """Créer un nouveau produit"""
        data = request.json
        champomi = Champomi(name=data['name'], price=data['price'], description=data.get('description'))
        session.add(champomi)
        session.commit()
        return {'id': champomi.id, 'name': champomi.name, 'price': float(champomi.price), 'description': champomi.description}, 201

@ns_champomi.route('/<int:id>')
@ns_champomi.response(404, 'Champomi non trouvé')
@ns_champomi.param('id', 'ID du produit')
class ChampomiResource(Resource):
    @ns_champomi.doc('get_champomi')
    def get(self, id):
        """Retourner un produit par son ID"""
        champomi = session.query(Champomi).get(id)
        if not champomi:
            return {'message': 'Champomi non trouvé'}, 404
        return {'id': champomi.id, 'name': champomi.name, 'price': float(champomi.price), 'description': champomi.description}, 200

    @ns_champomi.doc('update_champomi')
    @ns_champomi.expect(champomi_model)
    def put(self, id):
        """Mettre à jour complètement un produit"""
        champomi = session.query(Champomi).get(id)
        if not champomi:
            return {'message': 'Champomi non trouvé'}, 404
        data = request.json
        champomi.name = data['name']
        champomi.price = data['price']
        champomi.description = data.get('description')
        session.commit()
        return {'id': champomi.id, 'name': champomi.name, 'price': float(champomi.price), 'description': champomi.description}, 200

    @ns_champomi.doc('delete_champomi')
    def delete(self, id):
        """Supprimer un produit"""
        champomi = session.query(Champomi).get(id)
        if not champomi:
            return {'message': 'Champomi non trouvé'}, 404
        session.delete(champomi)
        session.commit()
        return {'message': 'Champomi supprimé'}, 200

if __name__ == '__main__':
    app.run(debug=True)
