from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSON
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def is_number(string):
    if string.replace(".", "").isnumeric():
        return True
    else:
        return False

app = Flask(__name__)
app.config['SECRET_KEY']='secret'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_HOST')

db=SQLAlchemy(app)

class Requisicao(db.Model):
    _tablename_= "requisicao"

    id_rek = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float)

class UltimaRequisicao(db.Model):
    _tablename_ = "ultima_requisicao"

    id_last_req = db.Column(db.Integer, primary_key=True)
    last_req = db.Column(db.Integer)

class Total(db.Model):
    _tablename_ = "total"
    
    id_total = db.Column(db.Integer, primary_key=True)
    total = db.Column(db.Float)

class Clima(db.Model):
    _tablename_ = "clima"

    id_clima = db.Column(db.Integer, primary_key=True)
    temperatura = db.Column(db.Float)
    umidade = db.Column(db.Integer)
    horario = db.Column(db.DateTime)

    def __init__(self, temperatura, umidade, horario):
        self.temperatura = temperatura
        self.umidade = umidade
        self.horario = horario

class CulturaReq(db.Model):
    _tablename_ = "requisicao_cultura"

    id_cultura_req = db.Column(db.Integer, primary_key=True)
    valor = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    horario = db.Column(db.Time, nullable=False)

    def __init__(self, valor, tipo, horario):
        self.valor = valor
        self.tipo = tipo
        self.horario = horario

with app.app_context():
    db.create_all()

@app.route('/req', methods=['GET', 'POST'])
def get():
    if request.method == "POST":
        try: 
            json = request.get_json()
            valor = Requisicao(valor=float(json['valor']))
            db.session.add(valor)
            db.session.commit()
            return jsonify({'message': 'Enviado com sucesso'})
        
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify({'message' : 'Falha ao enviar'})

    if request.method == "GET":
        obj = Requisicao.query.order_by(Requisicao.id_req.desc()).limit(1).first()
        resposta = jsonify({"id_valor": obj.id_req, "valor": obj.valor})
        return resposta

@app.route('/last-req', methods=['POST', 'GET'])
def req():
    if request.method == "POST":
        json = request.get_json()
        last_req = UltimaRequisicao(last_req=int(json['last_req']))
        db.session.add(last_req)
        db.session.commit()
        return jsonify({"last_req": last_req.last_req})
    
    if request.method == "GET":
        resposta = UltimaRequisicao.query.order_by(UltimaRequisicao.id_last_req.desc()).limit(1).first()
        return jsonify({"last_req": resposta.last_req})

@app.route('/total', methods=['POST'])
def total():
    if request.method == "POST":
        json = request.get_json()
        total = Total(total=float(json["total"]))
        if Total.query.first() is None:
            db.session.add(total)
            db.session.commit()
            return jsonify({'total': total.total})
        else:
            tot_atual = Total.query.order_by(Total.id_total.desc()).first()
            novo_total = total.total + tot_atual.total
            db_total = Total(total=float(novo_total))
            db.session.add(db_total)
            db.session.commit()
            return jsonify({'total': novo_total})

@app.route('/clima', methods=['POST', 'GET'])
def clima():
    if request.method == "POST":
        json = request.get_json()
        print(json)
        if is_number(str(json['temperatura'])) and is_number(str(json['umidade'])):
            try:
                dados = Clima(json['temperatura'], json['umidade'], datetime.now())
                db.session.add(dados)
                db.session.commit()
                return jsonify({'message': 'Enviado com sucesso'})
            
            except Exception as e:
                print(e)
                db.session.rollback()
                return jsonify({'message': 'Falha ao enviar'})
        else:
            return jsonify({'message': 'Dados não compatíveis'})

    if request.method == "GET":
        return render_template('index.html', dados=Clima.query.order_by(Clima.id_clima.desc()).limit(40).all())


@app.route('/getClima', methods=['GET'])
def getClima():
    if request.method == "GET":
        resposta = Clima.query.order_by(Clima.id_clima.desc()).limit(1).first()
        return jsonify({'temperatura': resposta.temperatura, 'umidade': resposta.umidade})
    
@app.route('/reqCultura', methods=['POST', 'GET'])
def reqCultura():
    if request.method == "POST":
        json = request.get_json()
        print(json)
        try:
            horario_str = json['horario']
            horario = datetime.strptime(horario_str, '%H:%M').time()
            dados = CulturaReq(json['valor'], json['tipo'], horario)
            db.session.add(dados)
            db.session.commit()
            return jsonify({'message': 'Enviado com sucesso'})
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify({'message': 'Falha ao enviar'})
        
    if request.method == "GET":
        querry = CulturaReq.query.order_by(CulturaReq.id_cultura_req.desc()).limit(1).first()
        print(querry)
        return jsonify({'tipo': querry.tipo, 'valor': querry.valor, 'horario': str(querry.horario)})


if __name__ == "main":
    app.run(debug=True)
