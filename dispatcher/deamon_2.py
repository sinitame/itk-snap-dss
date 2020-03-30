import requests, os, glob, argparse, time
import logging
from utils.workspace import Workspace
from utils.itk_snap_logger import ITKSnapHandler

###################################################################################################
#                           Setting logger
###################################################################################################

logger = logging.getLogger('Nodule Detection')
logging.basicConfig(format='%(asctime)s - %(name)s - (%(levelname)s) : %(message)s', \
                            level=logging.INFO, \
                            datefmt='%m/%d/%Y %I:%M:%S %p')

# Setting stream logger
stream_logger = logging.StreamHandler()
stream_logger.setLevel(logging.DEBUG)
logger.addHandler(stream_logger)


server_url="http://itk.10.7.11.23.nip.io"
service_url="http://nodule-detection-api.10.7.11.23.nip.io"
service_hash="e9330a9cb133785e73efa95157b73919bb380ccd"
provider="IBM-LAB"

INFERENCE_TIMEOUT = 180 # time in seconds
REQUESTS_INTERVAL = 10 # time in seconds

def log_progress(ticket_id, progress):
    log_progress_api = "{0}/api/pro/tickets/{1}/progress".format(main_url, ticket_id)
    log_response = requests.post(log_progress_api, data={"chunk_start":"0.0","chunk_end":"1.0","progress":str(progress)})
    logger.debug('Notified log progress {0} for ticket {1}: '.format(progress, ticket_id),log_response.text)

while True:
    files_to_process=[]
    loaded_files=[]
    processed_files=[]
    files_to_upload=[]

    ###################################################################################################
    #                           Claiming ticket and loading data
    ###################################################################################################

    claim_api_url = "{0}/api/pro/services/claims".format(server_url)

    claim_response = requests.post(claim_api_url, data={"services":service_hash,"provider":provider,"code":"01"})
    claim_response_content = claim_response.content.decode('utf-8')

    if claim_response_content=='None':
        logger.info("Waiting for ticket")
        time.sleep(10)
    else:
        # Setting ticket info
        ticket_id = claim_response_content.split(",")[0]
        ticket_directory = "/datastore/tickets/{0}".format('%08d' % int(ticket_id))

        # Setting ITK Snap logger to log in server API for the ticket
        ticket_logger = ITKSnapHandler(server_url, ticket_id)
        ticket_logger.setLevel(logging.INFO)
        logger.addHandler(ticket_logger)

        ticket_input_directory = os.path.join(ticket_directory, "input")
        loaded_files = glob.glob("{0}/*".format(ticket_input_directory))
        logger.info("Files received : ready for processing")

        #####################################################################################################
        #                                           Process data
        #####################################################################################################

        for file in loaded_files:
            if file.endswith(".itksnap"):
                workspace = Workspace(file)
            else:
                files_to_process.append(file)

        logger.debug("Workspace file:" + workspace.file_name)
        logger.debug("Files to process:" + ",".join(files_to_process))

        logger.info("Starting inference")

        for i, file in enumerate(files_to_process):
            inference_ready = False
            inference_failed = False
            inference_timeout = INFERENCE_TIMEOUT

            service_request_url = "{}/inference".format(service_url)
            with open(file, 'rb') as f:
                r = requests.post(service_request_url, files={"itk_image": f})

            # Setting infos for result file creation
            file_name_with_ext = os.path.basename(file)
            file_name = file_name_with_ext.split(".")[0]
            os.makedirs(os.path.join(ticket_directory, "results"), exist_ok=True)
            result_file_path = os.path.join(ticket_directory, "results", file_name + "_mask.nrrd")

            try:
                result_endpoint = r.json()["Endpoint"]
                logger.debug('Endpoint :' + result_endpoint)

                while (not inference_ready) and (inference_time < inference_timeout):
                    r = request.get(service_url + result_endpoint)

                    if r.status_code == 200:
                        inference_ready = True

                    inference_time += REQUESTS_INTERVAL
                    sleep(REQUESTS_INTERVAL)

                if inference_ready:
                    open(result_file_path, 'wb').write(r.content)
                    processed_files.append(result_file_path)

                else:
                    raise("Inference timeout exceeded")

            except Exception as e:
                logger.error(e)
                error_url = "{0}/api/pro/tickets/{1}/status".format(server_url, ticket_id)
                r = requests.post(error_url, data={"status":"failed"})
                logger.debug("Notify client of failure: " + r.text)
                logger.removeHandler(ticket_logger)
                inference_failed = True


        #######################################################################################################
        #                       Modify ITK snap workspace to integrate segmentation 
        #######################################################################################################

        if not(inference_failed):
            logger.info("Starting workspace update")
            for file in processed_files:
                file_name = file.split('/')[-1]
                logger.info("Adding {0} to workspace".format(file_name))
                workspace.add_segmentation(ticket_directory, file_name)

        #######################################################################################################
        #                           Notify client that the ticket is ready
        #######################################################################################################

        if not(inference_failed):
            logger.info("End processing")
            success_url = "{0}/api/pro/tickets/{1}/status".format(server_url, ticket_id)
            r = requests.post(success_url, data={"status": "success"})
            logger.debug("Notify client: " + r.text)


        logger.removeHandler(ticket_logger)
