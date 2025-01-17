from flask import Flask, jsonify, request
from flask_restx import Api, Resource, fields
from sqlalchemy import create_engine, Column, Integer, String, Numeric, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relationship, backref
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
api = Api(app, version='1.0', title='Champomix API',
          description='API REST pour la gestion de la base Champomix')

# Configuration de la base de données
DATABASE_URL = "postgresql://ug4uwcbl5qnrmkdujtl4:MVIoSCckMDQANgNOiCEG1sB94lmPw5@baqutj74xmaqvezj2pbz-postgresql.services.clever-cloud.com:50013/baqutj74xmaqvezj2pbz"
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

# Modèle Order
class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

orders = relationship('Order', backref=backref('user', cascade='all, delete-orphan'), cascade='all, delete')

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

# Modèle pour Swagger
user_model = api.model('User', {
    'id': fields.Integer(readOnly=True, description='ID unique de l\'utilisateur'),
    'pseudo': fields.String(required=True, description='Pseudo de l\'utilisateur'),
    'password': fields.String(required=True, description='Mot de passe de l\'utilisateur')
})

# Modèle pour Swagger
order_model = api.model('Order', {
    'id': fields.Integer(readOnly=True, description='ID unique de la commande'),
    'user_id': fields.Integer(required=True, description='ID de l\'utilisateur associé')
})

# Namespace pour Orders
ns_order = api.namespace('orders', description='Opérations sur les commandes')

# Namespace pour Users
ns_user = api.namespace('users', description='Opérations sur les utilisateurs')

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
        return {'id': champomi.id, 'name': champomi.name, 'price': float(champomi.price), 'description': champomi.description}, 201

    @ns_champomi.doc('delete_champomi')
    def delete(self, id):
        """Supprimer un produit"""
        champomi = session.query(Champomi).get(id)
        if not champomi:
            return {'message': 'Champomi non trouvé'}, 404
        session.delete(champomi)
        session.commit()
        return {'message': 'Champomi supprimé'}, 204

ns_user = api.namespace('users', description='Opérations sur les utilisateurs')

@ns_user.route('/')
class UserList(Resource):
    @ns_user.doc('list_users')
    def get(self):
        """Retourner la liste de tous les utilisateurs"""
        users = session.query(User).all()
        return [
            {
                'id': u.id,
                'pseudo': u.pseudo,
                'password': u.password
            } for u in users
        ], 200

    @ns_user.doc('create_user')
    @ns_user.expect(user_model)
    def post(self):
        """Créer un nouvel utilisateur"""
        data = request.json
        user = User(pseudo=data['pseudo'], password=data['password'])
        session.add(user)
        session.commit()
        return {'id': user.id, 'pseudo': user.pseudo, 'password': user.password}, 201

@ns_user.route('/<int:id>')
@ns_user.response(404, 'Utilisateur non trouvé')
@ns_user.param('id', 'ID de l\'utilisateur')
class UserResource(Resource):
    @ns_user.doc('get_user')
    def get(self, id):
        """Retourner un utilisateur par son ID"""
        user = session.query(User).get(id)
        if not user:
            return {'message': 'Utilisateur non trouvé'}, 404
        return {'id': user.id, 'pseudo': user.pseudo, 'password': user.password}, 200

    @ns_user.doc('update_user')
    @ns_user.expect(user_model)
    def put(self, id):
        """Mettre à jour complètement un utilisateur"""
        user = session.query(User).get(id)
        if not user:
            return {'message': 'Utilisateur non trouvé'}, 404
        data = request.json
        user.pseudo = data['pseudo']
        user.password = data['password']
        session.commit()
        return {'id': user.id, 'pseudo': user.pseudo, 'password': user.password}, 201

    @ns_user.doc('delete_user')
    def delete(self, id):
        """Supprimer un utilisateur"""
        user = session.query(User).get(id)
        if not user:
            return {'message': 'Utilisateur non trouvé'}, 404
        session.delete(user)
        session.commit()
        return {'message': 'Utilisateur supprimé'}, 204

@ns_user.route('/')
class UserList(Resource):
    @ns_user.doc('list_users')
    def get(self):
        """Retourner la liste de tous les utilisateurs"""
        users = session.query(User).all()
        return [
            {
                'id': u.id,
                'pseudo': u.pseudo,
                'password': u.password
            } for u in users
        ], 200

    @ns_user.doc('create_user')
    @ns_user.expect(user_model)
    def post(self):
        """Créer un nouvel utilisateur"""
        data = request.json
        user = User(pseudo=data['pseudo'], password=data['password'])
        session.add(user)
        session.commit()
        return {'id': user.id, 'pseudo': user.pseudo, 'password': user.password}, 201

@ns_user.route('/<int:id>')
@ns_user.response(404, 'Utilisateur non trouvé')
@ns_user.param('id', 'ID de l\'utilisateur')
class UserResource(Resource):
    @ns_user.doc('get_user')
    def get(self, id):
        """Retourner un utilisateur par son ID"""
        user = session.query(User).get(id)
        if not user:
            return {'message': 'Utilisateur non trouvé'}, 404
        return {'id': user.id, 'pseudo': user.pseudo, 'password': user.password}, 200

    @ns_user.doc('update_user')
    @ns_user.expect(user_model)
    def put(self, id):
        """Mettre à jour complètement un utilisateur"""
        user = session.query(User).get(id)
        if not user:
            return {'message': 'Utilisateur non trouvé'}, 404
        data = request.json
        user.pseudo = data['pseudo']
        user.password = data['password']
        session.commit()
        return {'id': user.id, 'pseudo': user.pseudo, 'password': user.password}, 201

    @ns_user.doc('delete_user')
    def delete(self, id):
        """Supprimer un utilisateur"""
        user = session.query(User).get(id)
        if not user:
            return {'message': 'Utilisateur non trouvé'}, 404

        # Supprimer les commandes associées à l'utilisateur
        orders = session.query(Order).filter(Order.user_id == id).all()
        for order in orders:
            session.delete(order)

        session.delete(user)
        session.commit()
        return {'message': 'Utilisateur et ses commandes associés supprimés'}, 204

# Ajouter le namespace à l'API
api.add_namespace(ns_user)

@ns_order.route('/')
class OrderList(Resource):
    @ns_order.doc('list_orders')
    def get(self):
        """Retourner la liste de toutes les commandes"""
        orders = session.query(Order).all()
        return [
            {
                'id': o.id,
                'user_id': o.user_id
            } for o in orders
        ], 200

    @ns_order.doc('create_order')
    @ns_order.expect(order_model)
    def post(self):
        """Créer une nouvelle commande"""
        data = request.json

        # Vérifier si l'utilisateur existe
        user = session.query(User).get(data['user_id'])
        if not user:
            return {'message': 'Utilisateur non trouvé'}, 404

        # Créer la commande
        order = Order(user_id=data['user_id'])
        session.add(order)
        session.commit()
        return {'id': order.id, 'user_id': order.user_id}, 201

@ns_order.route('/<int:id>')
@ns_order.response(404, 'Commande non trouvée')
@ns_order.param('id', 'ID de la commande')
class OrderResource(Resource):
    @ns_order.doc('get_order')
    def get(self, id):
        """Retourner une commande par son ID"""
        order = session.query(Order).get(id)
        if not order:
            return {'message': 'Commande non trouvée'}, 404
        return {'id': order.id, 'user_id': order.user_id}, 200

    @ns_order.doc('update_order')
    @ns_order.expect(order_model)
    def put(self, id):
        """Mettre à jour complètement une commande"""
        order = session.query(Order).get(id)
        if not order:
            return {'message': 'Commande non trouvée'}, 404
        data = request.json
        order.user_id = data['user_id']
        session.commit()
        return {'id': order.id, 'user_id': order.user_id}, 201

    @ns_order.doc('delete_order')
    def delete(self, id):
        """Supprimer une commande"""
        order = session.query(Order).get(id)
        if not order:
            return {'message': 'Commande non trouvée'}, 404
        session.delete(order)
        session.commit()
        return {'message': 'Commande supprimée'}, 204

if __name__ == '__main__':
    app.run(debug=True)