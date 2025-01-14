from flask import Blueprint, render_template, request, jsonify

# Création d'un blueprint pour les routes
main = Blueprint('main', __name__)

# Simuler une galerie et un panier
cart = []
images = [
    "/static/daniel-j-schwarz-Qhnsv_Ey2mA-unsplash.jpg",
    "/static/whoisbenjamin-K-2J2Zq2n6c-unsplash.jpg",
]

@main.route('/')
def index():
    return render_template('index.html', images=images)

@main.route('/cart')
def cart_view():
    return render_template('cart.html', cart=cart)

@main.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    image = data['image']
    quantity = int(data['quantity'])
    # Ajouter ou mettre à jour l'article dans le panier
    for item in cart:
        if item['image'] == image:
            item['quantity'] += quantity
            break
    else:
        cart.append({'image': image, 'quantity': quantity})
    return jsonify({'image': image, 'quantity': quantity})
