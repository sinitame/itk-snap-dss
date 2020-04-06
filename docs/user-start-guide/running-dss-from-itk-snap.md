## Running DSS from ITK-SNAP

1. After running ITK-snap (version `>=3.8.0`), open an image by clicking `File > Open Main Image ...`. ![ITK-SNAP Open Main Image](images/open_main_image.png)
1. Open the Distributed Segmentation Service window by clicking `Tools > Distributed Segmentation Service...`. ![ITK-SNAP Open DSS window](images/open_dss.png)
1. Connect to your ITK-SNAP DSS Server: ![ITK-SNAP Setup DSS Server Connexion](images/dss_server_url.png)
    1. Click `Manage...` and type your server URL.
    1. Click `Get Token`, then type the access token in the `Login Token` input field.
1. Submit your image for processing: ![ITK-SNAP DSS Submit Image](images/dss_submit.png)
    1. GO to the `Submit` tab.
    1. Choose the segmentation service you want to use in the `Service` list.
    1. Click `Submit`, then chose where you want to save the ITK-snap workspace to upload.
1. Get updates on segmentation progress in real time ![ITK-SNAP DSS Progress Updates](images/dss_progress.png)
1. Download results as ITK-SNAP workspace by clicking `Download` when processing is finished. ![ITK-SNAP DSS Result](images/dss_result.png)