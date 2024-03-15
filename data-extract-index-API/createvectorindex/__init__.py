import logging

import azure.functions as func
from backend.azure_ai_vector_store import *
from backend.azure_ai_vector_index import *

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    #file_path = req.params.get('filePath')
    #category = req.params.get('category')
    req_body =  req.get_json()
    filePath = req_body.get('filePath')
    category = req_body.get('category')

    create_vector_index('resume','semantic_resume')


    if filePath:
        upload(filePath,'resume')
        upload(filePath,'semantic_resume')
        return func.HttpResponse(f"This HTTP triggered function executed successfully.",status_code=200)
    else:
        return func.HttpResponse(
             "Please pass a File Path and category on the query string or in the request body",
             status_code=400
        )
