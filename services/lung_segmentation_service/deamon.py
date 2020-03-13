import requests, os, time

import numpy as np
import pickle, nrrd, json
import SimpleITK as sitk
import torch
from torch.utils import data
import torch.optim as optim
import torch.nn as nn
from torch.nn import functional as F
from scipy import ndimage
from xml.dom import minidom
import argparse
import glob
import os

try:
    import model
    import predict
    from data import *
except:
    from . import model
    from . import predict
    from .data import *


main_url="http://itk.10.7.11.23.nip.io"
service_hash="6e8775d466d865ce30eab35aa6d9a871a5d39816"
provider="IBM-LAB"

def log_progress(ticket_id, progress):
    log_progress_api = "{0}/api/pro/tickets/{1}/progress".format(main_url, ticket_id)
    log_response = requests.post(log_progress_api, data={"chunk_start":"0.0","chunk_end":"1.0","progress":str(progress)})
    print('Notified log progress {0} for ticket {1}: '.format(progress, ticket_id),log_response.text)

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

def add_segmentation_to_workspace(workspace_file, file_name):
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

    new_workspace = open(workspace_file,"w")
    original_workspace.writexml(new_workspace, encoding="UTF-8")
    new_workspace.close()


while True:
    files_to_process=[]
    downloaded_files=[]
    processed_files=[]
    files_to_upload=[]

    ###################################################################################################
    #                           Claiming ticket and downloading data
    ###################################################################################################

    claim_api_url = "{0}/api/pro/services/claims".format(main_url)

    claim_response = requests.post(claim_api_url, data={"services":service_hash,"provider":provider,"code":"01"})
    claim_response_content = claim_response.content.decode('utf-8')

    if claim_response_content=='None':
        time.sleep(10)
    else:
        ticket_id = claim_response_content.split(",")[0]

        ticket_directory = "/service/datastore/ticket{0}".format(ticket_id)
        os.makedirs(ticket_directory, exist_ok=True)

        list_file_api_url = "{0}/api/pro/tickets/{1}/files/input".format(main_url,ticket_id)

        files_to_download = requests.get(list_file_api_url)
        print(files_to_download.text)

        for row in files_to_download.text.split('\n')[:-1]:
            file_id = row.split(',')[0]
            file_name = row.split(',')[1][:-1]
            file_url = "{0}/api/pro/tickets/{1}/files/input/{2}".format(main_url, ticket_id, file_id)
            download = requests.get(file_url)
            file_path = ticket_directory + "/" + file_name
            open(file_path, 'wb').write(download.content)

            print("Downloaded ", file_path)
            downloaded_files.append(file_path)

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

        print(downloaded_files)
        for file in downloaded_files:
            if file.endswith(".itksnap"):
                workspace_file = file
            else:
                files_to_process.append(file)

        print("Workspace file:", workspace_file)
        print("Files to process", files_to_process)

        for file in files_to_process:

            # Load scan
            scan_path, scan_id = os.path.split(file)
            scan_id = scan_id.split('.')[0]

            ct_scan, origin, orig_spacing = utils.load_itk(file)
            if verbose == True:
                print(scan_id, ":\n -> shape:", ct_scan.shape, "\n -> spacing:", orig_spacing)
            log_progress(ticket_id, 0.1)

            ct_scan, spacing = utils.prep_img_arr(ct_scan, orig_spacing)
            if verbose == True:
                print("CT-scan:\n -> shape:", ct_scan.shape, "\n -> spacing:", spacing)
            log_progress(ticket_id, 0.2)

            # Compute lungs mask
            mask = predict.predict(ct_scan, nb_classes, start_filters, model_path=model_path, threshold=threshold, erosion=erosion, verbose=verbose)
            log_progress(ticket_id, 0.6)

            # Resample mask
            mask = utils.resample(mask[0][0], spacing, orig_spacing)
            if threshold == True:
                mask[mask<=0] = 0
                mask[mask>0] = 1
                mask = mask.astype('uint8')
            if verbose == True:
                print("Mask:\n -> shape:", mask.shape, "\n -> spacing:", orig_spacing)
            log_progress(ticket_id, 0.8)


            # Write into ouput files (nrrd format)
            result_file_path = os.path.join(scan_path, scan_id + '_mask.nrrd')
            utils.write_itk(result_file_path, mask, origin, orig_spacing)
            log_progress(ticket_id, 1.0)

            processed_files.append(result_file_path)

        #######################################################################################################
        #                       Modify ITK snap workspace to integrate segmentation 
        #######################################################################################################

        for file in processed_files:
            file_name = file.split('/')[-1]
            print(file_name)
            add_segmentation_to_workspace(workspace_file, file_name)

        #######################################################################################################
        #                                   Send result to server 
        #######################################################################################################

        files_to_upload = processed_files + [workspace_file]
        print(files_to_upload)

        send_file_url = "{0}/api/pro/tickets/{1}/files/results".format(main_url, ticket_id)
        for file in files_to_upload:
            with open(file, 'rb') as f:
                r = requests.post(send_file_url, files={"myfile": f})
        print("Sending:", r.text)

        #######################################################################################################
        #                           Notify client that the ticket is ready
        #######################################################################################################

        success_url = "{0}/api/pro/tickets/{1}/status".format(main_url, ticket_id)
        r = requests.post(success_url, data={"status": "success"})
        print("Notify client:", r.text)
