import requests, os, glob, argparse, time
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

def create_IOHistory_node(file_minidom, segmentation_file_path):

    # Create new node structure
    IOHistory_node = file_minidom.createElement("folder")
    IOHistory_node.setAttribute("key", "IOHistory")

    label_image_folder = file_minidom.createElement("folder")
    label_image_folder.setAttribute("key", "LabelImage")

    entry_1 = file_minidom.createElement("entry")
    entry_1.setAttribute("key", "ArraySize")
    entry_1.setAttribute("value", "1")
    label_image_folder.appendChild(entry_1)

    entry_2 = file_minidom.createElement("entry")
    entry_2.setAttribute("key", "Element[0]")
    entry_2.setAttribute("value", segmentation_file_path)
    label_image_folder.appendChild(entry_2)

    IOHistory_node.appendChild(label_image_folder)

    return IOHistory_node

def create_segmentation_layer_node(file_minidom, segmentation_file_path):
    segmentation_layer_node = file_minidom.createElement("folder")
    segmentation_layer_node.setAttribute("key", "Layer[001]")

    entry_1 = file_minidom.createElement("entry")
    entry_1.setAttribute("key", "AbsolutePath")
    entry_1.setAttribute("value", segmentation_file_path)
    segmentation_layer_node.appendChild(entry_1)

    entry_2 = file_minidom.createElement("entry")
    entry_2.setAttribute("key", "Role")
    entry_2.setAttribute("value", "SegmentationRole")
    segmentation_layer_node.appendChild(entry_2)

    entry_3 = file_minidom.createElement("entry")
    entry_3.setAttribute("key", "Tags")
    entry_3.setAttribute("value", "")
    segmentation_layer_node.appendChild(entry_3)

    # Making IOHints folder node
    IOHints_folder = file_minidom.createElement("folder")
    IOHints_folder.setAttribute("key", "IOHints")

    entry_IOHints_folder = file_minidom.createElement("entry")
    entry_IOHints_folder.setAttribute("key", "Format")
    entry_IOHints_folder.setAttribute("value", "NRRD")
    IOHints_folder.appendChild(entry_IOHints_folder)

    segmentation_layer_node.appendChild(IOHints_folder)

    # Making layer metadata folder
    LayerMetaData_folder = file_minidom.createElement("folder")
    LayerMetaData_folder.setAttribute("key", "LayerMetaData")

    entry_LMD_1 = file_minidom.createElement("entry")
    entry_LMD_1.setAttribute("key", "Alpha")
    entry_LMD_1.setAttribute("value", "0")
    LayerMetaData_folder.appendChild(entry_LMD_1)

    entry_LMD_2 = file_minidom.createElement("entry")
    entry_LMD_2.setAttribute("key", "CustomNickName")
    entry_LMD_2.setAttribute("value", "")
    LayerMetaData_folder.appendChild(entry_LMD_2)

    entry_LMD_3 = file_minidom.createElement("entry")
    entry_LMD_3.setAttribute("key", "Sticky")
    entry_LMD_3.setAttribute("value", "1")
    LayerMetaData_folder.appendChild(entry_LMD_3)

    entry_LMD_4 = file_minidom.createElement("entry")
    entry_LMD_4.setAttribute("key", "Tags")
    entry_LMD_4.setAttribute("value", "")
    LayerMetaData_folder.appendChild(entry_LMD_4)

    segmentation_layer_node.appendChild(LayerMetaData_folder)

    return segmentation_layer_node

def find_file_path(original_workspace, file_name):
    entries = original_workspace.getElementsByTagName("entry")
    for entry in entries:
        if entry.getAttribute("key") == "SaveLocation":
            file_path = entry.getAttribute("value")
            return file_path + '/' + file_name
    return ""

def add_segmentation_to_workspace(ticket_path, workspace_file, file_name):
    original_workspace = minidom.parse(workspace_file)

    segmentation_file_path = find_file_path(original_workspace, file_name)
    print(segmentation_file_path)
    IOHistory_node = create_IOHistory_node(original_workspace, segmentation_file_path)
    segmentation_layer_node = create_segmentation_layer_node(original_workspace, segmentation_file_path)

    folders = original_workspace.getElementsByTagName("folder")
    for folder in folders:
        if folder.getAttribute("key") == "ProjectMetaData":
            folder.appendChild(IOHistory_node)
        elif folder.getAttribute("key") == "Layers":
            folder.appendChild(segmentation_layer_node)

    result_workspace_file = os.path.join(ticket_path, "results", os.path.basename(workspace_file))
    new_workspace = open(result_workspace_file,"w")
    original_workspace.writexml(new_workspace, encoding="UTF-8")
    new_workspace.close()


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
        workspace_file = ""

        print(loaded_files)
        for file in loaded_files:
            if file.endswith(".itksnap"):
                workspace_file = file
            else:
                files_to_process.append(file)

        print("Workspace file:", workspace_file)
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
                inference_time = 0
                result_endpoint = r.json()["Endpoint"]
                print(result_endpoint)

                while (not inference_ready) and (inference_time < inference_timeout):
                    r = requests.get(service_url + result_endpoint)

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
                add_segmentation_to_workspace(ticket_directory, workspace_file, file_name)

        #######################################################################################################
        #                           Notify client that the ticket is ready
        #######################################################################################################

        if not(inference_failed):
            log_info(ticket_id, "End processing")
            success_url = "{0}/api/pro/tickets/{1}/status".format(main_url, ticket_id)
            r = requests.post(success_url, data={"status": "success"})
            print("Notify client:", r.text)
