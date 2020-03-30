import requests, os, glob, argparse, time
from utils.workspace import Workspace
from xml.dom import minidom

main_url="http://itk.10.7.11.23.nip.io"
service_url="http://lung-segmentation-api.10.7.11.23.nip.io"
service_hash="6e8775d466d865ce30eab35aa6d9a871a5d39816"
provider="IBM-LAB"

INFERENCE_TIMEOUT = 180 # time in seconds
REQUESTS_INTERVAL = 10 # time in seconds

def log_progress(ticket_id, progress):
    log_progress_api = "{0}/api/pro/tickets/{1}/progress".format(main_url, ticket_id)
    log_response = requests.post(log_progress_api, data={"chunk_start":"0.0","chunk_end":"1.0","progress":str(progress)})
    print('Notified log progress {0} for ticket {1}: '.format(progress, ticket_id),log_response.text)

def log_info(ticket_id, info):
    log_url = "{0}/api/pro/tickets/{1}/info".format(main_url, ticket_id)
    r = requests.post(log_url, data={"message": info})
    print('Notified info ({0}) for ticker {1}: '.format(info, ticket_id), r.text)

while True:
    files_to_process=[]
    loaded_files=[]
    processed_files=[]
    files_to_upload=[]

    ###################################################################################################
    #                           Claiming ticket and loading data
    ###################################################################################################

    claim_api_url = "{0}/api/pro/services/claims".format(main_url)

    claim_response = requests.post(claim_api_url, data={"services":service_hash,"provider":provider,"code":"01"})
    claim_response_content = claim_response.content.decode('utf-8')

    if claim_response_content=='None':
        print("Nothing to do")
        time.sleep(10)
    else:
        print("Received ticket")
        ticket_id = claim_response_content.split(",")[0]
        ticket_directory = "/datastore/tickets/{0}".format('%08d' % int(ticket_id))

        ticket_input_directory = os.path.join(ticket_directory, "input")
        loaded_files = glob.glob("{0}/*".format(ticket_input_directory))
        print(loaded_files)
        log_info(ticket_id, "Files received : ready for processing")

        #####################################################################################################
        #                                           Process data
        #####################################################################################################

        nb_classes=1
        start_filters=32
        model_path="/service/lung_segmentation_model"
        threshold=True
        erosion=True
        verbose=True

        print(loaded_files)
        for file in loaded_files:
            if file.endswith(".itksnap"):
                workspace = Workspace(file)
            else:
                files_to_process.append(file)

        print("Workspace file:", workspace.file_name)
        print("Files to process", files_to_process)

        log_info(ticket_id, "Starting inference")

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
                result_endpoint = r.json["Endpoint"]
                print(result_endpoint)

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
                print(e)
                error_url = "{0}/api/pro/tickets/{1}/status".format(main_url, ticket_id)
                r = requests.post(error_url, data={"status":"failed"})
                print("Notify client of failure", r.text)
                inference_failed = True


        #######################################################################################################
        #                       Modify ITK snap workspace to integrate segmentation 
        #######################################################################################################

        if not(inference_failed):
            log_info(ticket_id, "Starting workspace update")
            for file in processed_files:
                file_name = file.split('/')[-1]
                print(file_name)
                workspace.add_segmentation(ticket_directory, file_name)

        #######################################################################################################
        #                           Notify client that the ticket is ready
        #######################################################################################################

        if not(inference_failed):
            log_info(ticket_id, "End processing")
            success_url = "{0}/api/pro/tickets/{1}/status".format(main_url, ticket_id)
            r = requests.post(success_url, data={"status": "success"})
            print("Notify client:", r.text)
