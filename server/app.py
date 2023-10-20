#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate

from models import db, Bakery, BakedGood

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Bakery GET-POST-PATCH-DELETE API</h1>'

@app.route('/bakeries')
def bakeries():

    bakeries = Bakery.query.all()
    bakeries_serialized = [bakery.to_dict() for bakery in bakeries]

    response = make_response(
        bakeries_serialized,
        200
    )
    return response

@app.route('/bakeries/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def bakery_by_id(id):
    if request.method =='GET':
        bakery = Bakery.query.filter_by(id=id).first()
        bakery_serialized = bakery.to_dict()

        response = make_response(
            bakery_serialized,
            200
        )
        return response
    
    elif request.method == 'PATCH':
        bakery = Bakery.query.filter_by(id=id).first()

        if bakery is None:
            return jsonify({"error": "Bakery not found"}), 404
        
        for attr in request.form:
            setattr(bakery, attr, request.form.get(attr))

        db.session.add(bakery)
        db.session.commit()

        bakery_dict = bakery.to_dict()

        response = make_response(
            jsonify(bakery_dict),
            200
        )

        return response
    
    # elif request.method == 'DELETE':
    #     bakery = Bakery.query.filter_by(id =id).first()

    #     if bakery is None:
    #         return jsonify({"error": "Bakery not found"}), 404
        

    #     db.session.delete(bakery)
    #     db.session.commit()

    #     return jsonify({"message": "Bakery deleted successfully"})

app.route('/baked_goods/<int:id>', methods=['DELETE'])
def delete_baked_good(id):
    baked_good = BakedGood.query.get(id)

    if baked_good is None:
        return jsonify({"error": "Baked good not found"}), 404

    # Delete the baked good from the database
    db.session.delete(baked_good)
    db.session.commit()

    return jsonify({"message": "Baked good deleted successfully"}), 200


@app.route('/baked_goods/by_price')
def baked_goods_by_price():
    baked_goods_by_price = BakedGood.query.order_by(BakedGood.price).all()
    baked_goods_by_price_serialized = [
        bg.to_dict() for bg in baked_goods_by_price
    ]
    
    response = make_response(
        baked_goods_by_price_serialized,
        200
    )
    return response

@app.route('/baked_goods/most_expensive')
def most_expensive_baked_good():
    most_expensive = BakedGood.query.order_by(BakedGood.price.desc()).limit(1).first()
    most_expensive_serialized = most_expensive.to_dict()

    response = make_response(
        most_expensive_serialized,
        200
    )
    return response

@app.route('/baked_goods', methods=['GET', 'POST'])
def baked_goods():
    if request.method == 'GET':
        baked_goods = []
        for baked_good in BakedGood.query.all():
            baked_good_dict = baked_good.to_dict()
            baked_goods.append(baked_good_dict)

        response = make_response(
            jsonify(baked_goods),
            200
        )

        return response
    
    elif request.method == 'POST':
        #Get data from request form
        name = request.form.get('name')
        price = request.form.get('price')
        bakery_id = request.form.get('bakery_id')

        if not name or not price or not bakery_id:
            return jsonify({"error": "Missing required data"}), 400
        
        baked_good = BakedGood(name=name, price=price, bakery_id=bakery_id)

        db.session.add(baked_good)

        db.session.commit()

        if baked_good.id is not None:
            response_body = baked_good.to_dict()
            response = make_response(
                jsonify(response_body),

                201
            )
            return response
        
        else:
            return jsonify({"error": "Failed to create baked good"}), 500

if __name__ == '__main__':
    app.run(port=5555, debug=True)
