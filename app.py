from flask import Flask, request, jsonify
import pymysql
from flask_cors import CORS
from web3 import Web3

app = Flask(__name__)
CORS(app)


class Database():
    def __init__(self):
        self.db = pymysql.connect(host='localhost',
                                  user='root',
                                  password='worldstar3',
                                  db='vote_system',
                                  charset='utf8')
        self.cursor = self.db.cursor(pymysql.cursors.DictCursor)

    def execute(self, query, args={}):
        self.cursor.execute(query, args)

    def executeOne(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchone()
        return row

    def executeAll(self, query, args={}):
        self.cursor.execute(query, args)
        row = self.cursor.fetchall()
        return row

    def commit(self):
        self.db.commit()


class Wallet:
    address = None
    private_key = None


class ETH(object):
    def __init__(self):
        self.w3 = Web3(Web3.HTTPProvider("https://ropsten.infura.io/v3/e316220caec545259d80d76dc192c4b7"))

    def transfer(self, data):
        wallet = Wallet()
        with open('wallet/address', 'r') as address:
            wallet.address = address.read()
        with open('wallet/private_key', 'r') as private_key:
            wallet.private_key = private_key.read()

        try:
            signed_txn = self.w3.eth.account.signTransaction(dict(
                nonce=self.w3.eth.getTransactionCount(wallet.address),
                gasPrice=self.w3.eth.gasPrice,
                gas=100000,
                to=wallet.address,
                value=Web3.toWei(0, 'ether'),
                data=data.encode()
            ),
                eval(wallet.private_key))

            self.w3.eth.sendRawTransaction(signed_txn.rawTransaction)

            return jsonify({
                "success": True,
                "msg": "ETH pending Successfully!!",
            }), 200
        except ValueError as e:
            return jsonify({
                "success": False,
                "msg": "Not enough ETH!!",
            }), 200


@app.route('/vote/new', methods=['GET'])
def vote_new():
    name = request.args.get('name')
    tel = request.args.get('tel')
    introduce = request.args.get('introduce')
    count = 0

    if name is not None and tel is not None and introduce is not None:
        try:
            db = Database()
            sql = "INSERT INTO candidate VALUES('{}', '{}', '{}', '{}')".format(name, tel, introduce, count)
            db.execute(sql)
            db.commit()
            return jsonify({"status": True}), 200
        except pymysql.err.IntegrityError:
            return jsonify({"status": False}), 200
    else:
        return jsonify({"status": False}), 200


@app.route('/vote/voting', methods=['GET'])
def vote_voting():
    candidate_name = request.args.get('candidate_name')
    candidate_tel = request.args.get('candidate_tel')
    user_name = request.args.get('user_name')
    user_tel = request.args.get('user_tel')

    db = Database()
    try:
        sql_get_count = "SELECT count FROM candidate WHERE name='{}' AND tel='{}'".format(candidate_name, candidate_tel)
        row = db.executeAll(sql_get_count)[0]['count'] + 1
        sql_insert_user = "INSERT INTO user VALUES('{}', '{}')".format(user_name, user_tel)
        db.execute(sql_insert_user)
        db.commit()
        sql_update_count = "UPDATE candidate SET count = {} WHERE name='{}' AND tel='{}'".format(row, candidate_name, candidate_tel)
        db.execute(sql_update_count)
        db.commit()

        eth = ETH()
        print(eth.transfer("candidate : {}-{} / user : {}-{}".format(candidate_name, candidate_tel, user_name, user_tel)))

        return jsonify({"status": True}), 200
    except IndexError:
        return jsonify({
            "status": False,
            "message": "존재하지 않는 후보자입니다."
        }), 200
    except pymysql.err.IntegrityError:
        return jsonify({
            "status": False,
            "message": "이미 투표한 사용자입니다."
        }), 200

@app.route('/vote/check', methods=['GET'])
def vote_check():
    db = Database()
    sql = "SELECT * FROM candidate"
    row = db.executeAll(sql)
    return jsonify(row), 200


if __name__ == '__main__':
    app.run(debug=True)
