#!/bin/python3
from client import *

class admin():
    def __init__(self):
        pass

    def addColonna(self, colonna, citta, indirizzo, fornitore, fee, id,disp):
        logging.info('addColonna({})'.format(id))
        input_address_list = [COLONNE_TABLE]
        output_address_list = [COLONNE_TABLE,getColonneAddress(id)]
        logging.info("\nID:"+id+"\n"+str(output_address_list)+"\n")
        colonne = [colonna, citta, indirizzo, fornitore, fee, id,disp]
        colonnaArgs = ",".join(colonne)
        response = wrap_and_send(
            "addColonna", colonnaArgs, input_address_list, output_address_list, wait=5)
        try:
            result = yaml.safe_load(response)['data'][0]['status']
        except:
            result = "ERRORE"
        logging.info("Result: "+result)
        return result
    
    def removeCol(self,id):
        logging.info('removeColonna({})'.format(id))
        input_address_list = [COLONNE_TABLE,getColonneAddress(id)]
        output_address_list = [COLONNE_TABLE,getColonneAddress(id)]
        logging.info("\nID:"+id+"\n"+str(output_address_list)+"\n")
        colonnaArgs = ",".join(id)
        response = wrap_and_send(
            "removeCol", colonnaArgs, input_address_list, output_address_list, wait=5)
        try:
            result = yaml.safe_load(response)['data'][0]['status']
        except:
            result = "ERRORE"
        logging.info("Result: "+result)
        return result


    def rent(self,id,state):
        logging.info('rent({})'.format(id))
        input_address_list = [COLONNE_TABLE,getColonneAddress(id)]
        output_address_list = [COLONNE_TABLE,getColonneAddress(id)]
        logging.info("\nID: "+id+"\n"+str(output_address_list)+"\n")
        colonnaArgs = ",".join(id)
        if state == "true":

            response = wrap_and_send(
                "rent", colonnaArgs, input_address_list, output_address_list, wait=5)
        elif state == "false":
            response = wrap_and_send(
                "cancel", colonnaArgs, input_address_list, output_address_list, wait=5)
        try:
            result = yaml.safe_load(response)['data'][0]['status']
        except:
            result = "Qualcosa è andato storto, sei sicuro che la colonna sia disponibile?"
            logging.info("Result: "+result)
        return result

    def listClients(self, clientAddress):
        result = send_to_rest_api("state/{}".format(clientAddress))
        try:
            return (base64.b64decode(yaml.safe_load(result)["data"])).decode()
        except BaseException:
            return None

    def listCol(self):
        return listClients(COLONNE_TABLE)
