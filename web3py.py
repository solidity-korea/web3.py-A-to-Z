from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from web3 import Web3, HTTPProvider, IPCProvider
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
db = SQLAlchemy(app)
w3 = Web3(HTTPProvider('http://localhost:7545'))  # http://host:port
w3.eth.enable_unaudited_features()


# models.py
class Wallet(db.Model):
    __tablename__ = 'wallets'
    id = db.Column(db.Integer, primary_key=True)

    address = db.Column(db.String(40), unique=True, nullable=False)
    private_key = db.Column(db.String(152), unique=True, nullable=False)
    created_at = db.Column(
        db.DateTime,
        default=func.now(),
    )
    account = None

    def __init__(self, address, private_key):  # default morecoin
        if address.startswith('0x'):
            address = address[2:]
        if private_key.startswith('0x'):
            private_key = private_key[2:]
        self.address = address
        self.private_key = private_key


    @staticmethod
    def create_account(salt=None):
        if not salt:
            salt = os.urandom(16)

        account = w3.eth.account.create(salt)
        wallet = Wallet(address=account.address, private_key=account.privateKey.hex())
        db.session.add(wallet)
        db.session.commit()
        return wallet


# view.py
@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/keystore')
def list_keystore():

    output = ''
    for k in w3.personal.listAccounts:
        output += k
        output += ' '
        output += str(w3.eth.getBalance(k))  # to from wei

        output += '<br>'

    return output


@app.route('/create_account')
def create_account():
    wallet = Wallet.create_account('test_salt')
    print(wallet.address, wallet.private_key)
    return wallet.address
    # return 'Hello World!'


@app.route('/wallets')
def list_wallet():
    wallets = Wallet.query.all()
    output = ''
    for w in wallets:
        output += w.address
        output += ' '
        output += w.private_key
        # balance
        output += '<br>'
    return output

# manage.py
if __name__ == '__main__':
    db.create_all()
    app.run(port=8080)
