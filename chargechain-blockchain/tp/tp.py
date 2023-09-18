#!/usr/bin/python3
import traceback
import sys
import hashlib
import logging

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.core import TransactionProcessor

DEFAULT_URL = 'tcp://validator:4004'

def hash(data):
    return hashlib.sha512(data.encode()).hexdigest()

logging.basicConfig(filename='tp.log',level=logging.DEBUG)
LOGGER = logging.getLogger(__name__)

# namespaces
family_name = "ChargeChain"
FAMILY_NAME = hash(family_name)[:6]

TABLES = hash("tables")[:6]

TRACKING = hash("tracking")[:6]
TRACKING_TABLE = FAMILY_NAME + TRACKING

COLONNE_ENTRIES = hash("colonne-entries")[:6]
COLONNE = hash("colonne")
COLONNE_TABLE = FAMILY_NAME + TABLES + COLONNE[:58]


def getBatchAddress(batchID):
    return TRACKING_TABLE + hash(batchID)[:58]

def getColonnaAddress(id):
    return FAMILY_NAME + COLONNE_ENTRIES + hash(id)[:58]


class ChainChargeHandler(TransactionHandler):
    '''
    Transaction Processor class for the ChainCharge family
    '''
    def __init__(self, namespace_prefix):
        '''Initialize the transaction handler class.
        '''
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        '''Return Transaction Family name string.'''
        return family_name

    @property
    def family_versions(self):
        '''Return Transaction Family version string.'''
        return ['1.0']

    @property
    def namespaces(self):
        '''Return Transaction Family namespace 6-character prefix.'''
        return [self._namespace_prefix]

    # Get the payload and extract information.
    # It has already been converted from Base64, but needs deserializing.
    # It was serialized with CSV: action, value
    def _unpack_transaction(self, transaction):
        header = transaction.header
        payload_list = self._decode_data(transaction.payload)
        return payload_list

    def apply(self, transaction, context):
        '''This implements the apply function for the TransactionHandler class.
        '''
        LOGGER.info ('starting apply function')
        try:
            payload_set = self._unpack_transaction(transaction)
            payload_list =  list(payload_set)
            LOGGER.info ('payload: {}'.format(payload_list))
            action = payload_list[0]
            try:
                if action == "addColonna":
                    self._addColonna(context, payload_list)
                elif action == "removeCol":
                    id = ""
                    for t in payload_list[1:]:
                        id = id+t
                    self._removeCol(context, id)
                elif action == "rent":
                    id = ""
                    for t in payload_list[1:]:
                        id = id+t
                    self._rent(context, id)
                elif action == "cancel":
                    id = ""
                    for t in payload_list[1:]:
                        id = id+t
                    self._cancel(context, id)
                else:
                    LOGGER.debug("Unhandled action: " + action)
            except IndexError as i:
                LOGGER.debug ('IndexError: {}'.format(i))
                raise Exception()
        except Exception as e:
            raise InvalidTransaction("Error: {}".format(e))

   
    @classmethod
    def _addColonna(self, context, payload_list):
        try:
            newColonna = ""
            newColonna = str(payload_list[1])+","+str(payload_list[2])+","+str(payload_list[3])+","+str(payload_list[4])+","+str(payload_list[5])+","+str(payload_list[6])+","+str(payload_list[7])
            LOGGER.info("ADD COLONNA")
            list_colonne = self._readData(context, COLONNE_TABLE)
            for s in list_colonne:
                if s == "":
                    list_colonne.remove(s)
            LOGGER.info ('Lista Colonne: {}'.format(list_colonne))
            nuovo = "true"
            if list_colonne:
                for t in list_colonne:
                    tempfield = t.split(",")
                    if tempfield[5] == payload_list[6]:
                        raise InvalidTransaction(" Colonna già esistente")
                list_colonne.append(newColonna)
                #LOGGER.info ('colonne aggiornate: {}'.format(list_colonne))
                addresses  = context.set_state({
                                    getColonnaAddress(payload_list[6]): self._encode_data(newColonna)
                                })
                addresses  = context.set_state({
                            COLONNE_TABLE: self._encode_data(list_colonne)})

            else:
                list_colonne = newColonna
                addresses  = context.set_state({
                            COLONNE_TABLE: newColonna.encode()})
            
        except Exception as e:
            logging.debug ('excecption: {}'.format(e))
            raise InvalidTransaction("State Error")

    @classmethod
    def _removeCol(self, context, id):
        try:
            LOGGER.info("REMOVE COL")
            list_colonne = self._readData(context, COLONNE_TABLE)
            for s in list_colonne:
                if s == "":
                    list_colonne.remove(s)
            LOGGER.info ('Lista Colonne: {}'.format(list_colonne))
            newList = ""
            flag = False
            if list_colonne:
                for t in list_colonne:
                    tempfield = t.split(",")
                    if tempfield[5] != id:
                        newList = newList+t+"-"
                    else:
                        flag = True
                if flag == False:
                    raise InvalidTransaction(" Colonna non trovata")
                addresses  = context.set_state({
                COLONNE_TABLE: newList.encode()})

            else:
                raise InvalidTransaction("Nessuna Colonna disponibile")

            
        except Exception as e:
            logging.debug ('excecption: {}'.format(e))
            raise InvalidTransaction("State Error")

    @classmethod
    def _rent(self, context, id):
        try:
            LOGGER.info("RENT Col")
            list_colonne = self._readData(context, COLONNE_TABLE)
            for s in list_colonne:
                if s == "":
                    list_colonne.remove(s)
            LOGGER.info ('Lista Colonne: {}'.format(list_colonne))
            newList = ""
            rentValue = ""
            flag = False
            if list_colonne:
                for t in list_colonne:
                    tempfield = t.split(",")
                    if tempfield[5] == id:
                        flag = True
                        if tempfield[6] == "false":
                            raise InvalidTransaction("Colonna gia noleggia, non disponibile")
                        rentValue = t.replace("true","false")
                        newList = newList+rentValue+"-"
                    else:
                        newList = newList+t+"-"
                if flag==False:
                    raise InvalidTransaction("Colonna non trovata")

                LOGGER.info ('Lista : {}'.format(newList))
                addresses  = context.set_state({
                COLONNE_TABLE: newList.encode()})
            else:
                raise InvalidTransaction("Nessuna Colonna disponibile")
        except Exception as e:
            logging.debug ('excecption: {}'.format(e))
            raise InvalidTransaction("State Error")


    @classmethod
    def _cancel(self, context, id):
        try:
            LOGGER.info("Disdici Col")
            list_colonne = self._readData(context, COLONNE_TABLE)
            for s in list_colonne:
                if s == "":
                    list_colonne.remove(s)
            LOGGER.info ('colonnnnnnnne: {}'.format(list_colonne))
            newList = ""
            rentValue = ""
            flag = False
            if list_colonne:
                for t in list_colonne:
                    tempfield = t.split(",")
                    if tempfield[5] == id:
                        flag = True
                        if tempfield[6] == "true":
                            raise InvalidTransaction("Colonna gia disponibile")
                        rentValue = t.replace("false","true")
                        newList = newList+rentValue+"-"
                    else:
                        newList = newList+t+"-"
                if flag==False:
                    raise InvalidTransaction("Colonna non trovata")

                LOGGER.info ('Lista: {}'.format(newList))
                addresses  = context.set_state({
                COLONNE_TABLE: newList.encode()})
            else:
                raise InvalidTransaction("Nessuna Colonna disponibile")
        except Exception as e:
            logging.debug ('excecption: {}'.format(e))
            raise InvalidTransaction("State Error")
    
    # returns a list
    @classmethod
    def _readData(self, context, address):
        state_entries = context.get_state([address])
        if state_entries == []:
            return []
        LOGGER.info("Read Data:"+str(state_entries[0].data))
        try:
            data = self._decode_data_list(self,state_entries[0].data)
        except:
            traceback.print_exc() 
        return data

    # returns a list
    @classmethod
    def _decode_data(self, data):
        return data.decode().split(',')

    def _decode_data_list(self, data):
        return data.decode().split('-')

    # returns a csv string
    @classmethod
    def _encode_data(self, data):
        return  str("-".join(data)).encode()


def main():
    try:
        # Setup logging for this class.
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)

        # Register the Transaction Handler and start it.
        processor = TransactionProcessor(url=DEFAULT_URL)
        sw_namespace = FAMILY_NAME
        handler = ChainChargeHandler(sw_namespace)
        processor.add_handler(handler)
        processor.start()
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
