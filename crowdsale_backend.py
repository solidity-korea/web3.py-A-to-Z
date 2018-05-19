from flask import Flask, jsonify
from web3 import Web3, HTTPProvider, IPCProvider
import json

infura_provider = HTTPProvider('https://ropsten.infura.io')
w3 = Web3(infura_provider)


app = Flask(__name__)

crowdsale_contract_address = "0x5d45e49e43a1e89d8f1306dbc239328fa4ccf4a3"
crowdsale_contract_address = w3.toChecksumAddress(crowdsale_contract_address)  # https://github.com/ethereum/web3.py/issues/740

crowdsale_abi = json.load(open('abi_crowdsale.json','r'))
crowdsale = w3.eth.contract(
    address=crowdsale_contract_address,
    abi=crowdsale_abi,
)


def get_raised_rate(contract):
    return contract.functions.weiRaised().call() / contract.functions.cap().call() * 100


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/reach')
def reach():
    res = {}
    res['reach'] = get_raised_rate(crowdsale)
    return jsonify(res)


@app.route('/raised')
def raised():
    res = {}
    res['cap'] = crowdsale.functions.cap().call()
    res['weiRaised'] = crowdsale.functions.weiRaised().call()
    res['reach'] = res['weiRaised'] / res['cap'] * 100
    return jsonify(res)


# manage.py
if __name__ == '__main__':
    app.run(port=8080)
