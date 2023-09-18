#!/usr/bin/python3
import hashlib
import base64
import random
import time
import requests
import yaml
import sys
import logging
import optparse
from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch

logging.basicConfig(filename='client.log',level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

parser = optparse.OptionParser()
parser.add_option('-U', '--url', action = "store", dest = "url", default = "http://rest-api:8008")

def hash(data):
    return hashlib.sha512(data.encode()).hexdigest()

family_name = "ChargeChain"
FAMILY_NAME = hash(family_name)[:6]

TABLES = hash("tables")[:6]

TRACKING = hash("tracking")[:6]
TRACKING_TABLE = FAMILY_NAME + TRACKING

COLONNE_ENTRIES = hash("colonne-entries")[:6]
COLONNE = hash("colonne")
COLONNE_TABLE = FAMILY_NAME + TABLES + COLONNE[:58]


# random private key
context = create_context('secp256k1')
private_key = context.new_random_private_key()
signer = CryptoFactory(context).new_signer(private_key)
public_key = signer.get_public_key().as_hex()

base_url = 'http://rest-api:8008'

def getBatchAddress(batchID):
    return TRACKING_TABLE + hash(batchID)[:58]

def getColonneAddress(id):
    return FAMILY_NAME + COLONNE_ENTRIES + hash(id)[:58]


def listClients(clientAddress):
    result = send_to_rest_api("state/{}".format(clientAddress))
    try:
        logging.info("Result:"+result)
        return (base64.b64decode(yaml.safe_load(result)["data"])).decode()
    except BaseException:
        return None

def send_to_rest_api(suffix, data=None, content_type=None):
    url = "{}/{}".format(base_url, suffix)
    headers = {}
    logging.info ('sending to ' + url)

    if content_type is not None:
        headers['Content-Type'] = content_type
    try:

        if data is not None:
           
            result = requests.post(url, headers=headers, data=data)
        else:
            result = requests.get(url, headers=headers)
        if not result.ok:
            logging.debug ("Error {}: {}".format(result.status_code, result.reason))
            raise Exception("Error {}: {}".format(result.status_code, result.reason))
    except requests.ConnectionError as err:
        logging.debug ('Failed to connect to {}: {}'.format(url, str(err)))
        raise Exception('Failed to connect to {}: {}'.format(url, str(err)))
    except BaseException as err:
        raise Exception(err)
    logging.info("Result.text: "+result.text)
    return result.text

def wait_for_status(batch_id, result, wait = 10):
    '''Wait until transaction status is not PENDING (COMMITTED or error).
        'wait' is time to wait for status, in seconds.
    '''
    if wait and wait > 0:
        waited = 0
        start_time = time.time()
        logging.info ('url : ' + base_url + "/batch_statuses?id={}&wait={}".format(batch_id, wait))
        while waited < wait:
            
            result = send_to_rest_api("batch_statuses?id={}&wait={}".format(batch_id, wait))
            try:
                status = yaml.safe_load(result)['data'][0]['status']
            except:
           	   	status = "PENDING"
            waited = time.time() - start_time

            if status != 'PENDING':
                return result
        logging.debug ("Transaction timed out after waiting {} seconds.".format(wait))
        return "Transaction timed out after waiting {} seconds.".format(wait)
    else:
        return result


def wrap_and_send(action, data, input_address_list, output_address_list, wait=None):
    '''Create a transaction, then wrap it in a batch.
    '''
    payload = ",".join([action, str(data)])
    logging.info ('payload: {}'.format(payload))

    # Construct the address where we'll store our state.
    # Create a TransactionHeader.
    header = TransactionHeader(
        signer_public_key = public_key,
        family_name = family_name,
        family_version = "1.0",
        inputs = input_address_list,         # input_and_output_address_list,
        outputs = output_address_list,       # input_and_output_address_list,
        dependencies = [],
        payload_sha512 = hash(payload),
        batcher_public_key = public_key,
        nonce = random.random().hex().encode()
    ).SerializeToString()

    # Create a Transaction from the header and payload above.
    transaction = Transaction(
        header = header,
        payload = payload.encode(),                 # encode the payload
        header_signature = signer.sign(header)
    )

    transaction_list = [transaction]

    # Create a BatchHeader from transaction_list above.
    header = BatchHeader(
        signer_public_key = public_key,
        transaction_ids = [txn.header_signature for txn in transaction_list]
    ).SerializeToString()

    # Create Batch using the BatchHeader and transaction_list above.
    batch = Batch(
        header = header,
        transactions = transaction_list,
        header_signature = signer.sign(header)
    )

    # Create a Batch List from Batch above
    batch_list = BatchList(batches=[batch])
    batch_id = batch_list.batches[0].header_signature
    # Send batch_list to the REST API
    result = send_to_rest_api("batches", batch_list.SerializeToString(), 'application/octet-stream')

    # Wait until transaction status is COMMITTED, error, or timed out
    return wait_for_status(batch_id, result, wait = wait)
