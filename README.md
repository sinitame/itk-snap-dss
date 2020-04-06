# ITK-SNAP Distributed Segmentation Service (DSS) Middleware Layer

This is the source code of the middleware layer for the IBM ITK-SNAP distributed segmentation service (DSS) adapted from the open source [ITK-SNAP DSS project](https://github.com/pyushkevich/alfabis_server). 


[ITK-SNAP](itksnap.org) is an interactive tool for segmentation of volumetric medical imaging datasets, like CT and MRI. 
DSS is a web-based application that allows data-scientists to make their advanced image processing algorithms available as services to ITK-SNAP users. 

### Global architecture

![](imgs/global-architecture.png)

### Components details

**Web Server**

The web server as two main role in the Distributed Segmentation Service:
*  It's a web interface to visualize and manage available services, providers, ticket history and admin users. It also gives some informations about the different available services and about the DSS itself. The admin access is normally handled with OAuth2 but for testing purpose, a default user `test@example.com` have been created.
*  It's a RestAPI server that can receive tickets from ITK-Snap clients. It handles the different steps of the ticket processing logic and store them in a PosgresDB.

**Dispatcher**

The dispatcher is a set of deamons (one per service) that regularly check for new tickets on the server. When a ticket is available it is claimed by the corresponding deamon and the deamon handles all the steps required for ticket processing (data download, inference, workspace update, data upload).

**Inference server**

The inference server is the server that perform the different inference tasks (at this stage: `lung-segmantation` and `nodule-detection`). It exposes a REST API that can be reached by the dispacher through port `8080`.

## Getting started
 
### Prerequisites

This project have been deployed on an [Open Shift](https://www.openshift.com) cluster running with `v3.11.161`.
We give some example of the commands that we used on out Open Shift Container Platform (OCP) to deploy our project in the following parts, but this documentation aims to be enough generoc so you can adapt the deployment steps to match your own infrastructure.


Each components of the architecture is fully Dockerised and have specific requirements:

*  Web Server
    *  No specific hardware requirement
    *  Persistent volume
    *  Expose port `8080` to an accessible route
*  DB
    *  No specific hardware requirement
*  Dispatcher
    *  No specific hardware requirement
    *  Persistent volume
*  Inference Server:
    *  Power node (AC922) with a compatible GPU (see [docker image requirements](https://hub.docker.com/r/ibmcom/powerai) for more informations)
    *  Persistent volume mounted at `/wmlce/data/output`
    *  Expose port `8080` to an accessible route

### Shared volumes
In order to avoid data exchanges between the __Dispatcher__ and the __Web Server__, we set up a shared storage volume between the two components in order to make both of them access tickets inputs and outputs.
This shared volume needs to be created by setting up a persistent volume within the project that you can then mount into the two components.

Details about the directory where this persistent volume needs to be mounted are given in the following parts.

### Routes
Some of the components exposes ports (`8080` for REST APIs). Theses ports needs to be routed into an __accessible URL__ and the corresponding URLs need to be set up in some __environment variables__ (written `ENV_VARIABLES`) for the different components 

* **ITK-SNAP Server route:** route used to access the web-interface and contact de web server API (ours is `http://itk.10.7.11.23.nip.io`)
    * Needs to be updated in ITK-SNAP DSS service interface 
    * Needs to be updated in Dispatcher config :  `SERVER_URL`
* **Inference Server route:** route used to contact Inference Server API (ours is `http://inference-server.10.7.11.23.nip.io`)
    * Needs to be updated in Dispatcher config:
        * `LUNG_SEGMENTATION_SERVICE_URL`: route to inference server (ours is `http://inference-server.10.7.11.23.nip.io`)
        * `NODULE_DETECTION_SERVICE_URL`: route to inference server (ours is `http://inference-server.10.7.11.23.nip.io`)

### Image creation

* **Dispatcher deployment:** Create app from Dockerfile `dispatcher/Dockerfile`.
    * OCP example : `oc new-app --name itk-snap-dispatcher https://itk-snap-dss:2EVH6Ky6zJPL7wn7QAsq@gitlab.com/PSLC/ia-medical/itk-snap-dss.git --context-dir dispatcher`
    * Set-up shared volume: mount persistent volume in `/datastore`
    * Set-up environment variables: 
        * `SERVER_URL`
        * `LUNG_SEGMENTATION_SERVICE_URL`
        * `NODULE_DETECTION_SERVICE_URL`
* **PosgresDB deployment:** Create app from Dockerfile `db/Dockerfile` (note that db is not persistent in this configuration) .
    * OCP example: `oc new-app --name itk-snap-dc https://itk-snap-dss:2EVH6Ky6zJPL7wn7QAsq@gitlab.com/PSLC/ia-medical/itk-snap-dss.git --context-dir db`
    * Set-up environment variables:
        * `POSTGRES_HOST_AUTH_METHOD=true`
* **Server deployment:** Create app from Dockerfile `web-server/Dockerfile`.
    * OCP example `oc new-app --name itk-snap-web-server https://itk-snap-dss:2EVH6Ky6zJPL7wn7QAsq@gitlab.com/PSLC/ia-medical/itk-snap-dss.git --context-dir web-server`
    * Set-up shared volume: mount persistent volume in `/app/datastore`
    * Set-up environment variables:
        * `POSTGRES_PORT_5432_TCP_ADDR=itk-snap-db`
        * `POSTGRES_PORT_5432_TCP_PORT=5432`
        * `ITK_SNAP_SERVER_DATABASE_NAME=admin_db`
        * `ITK_SNAP_SERVER_DATABASE_USERNAME=admin_user`    
        * `ITK_SNAP_SERVER_DATABASE_PASSWORD=` (leave empty)
        * `ITK_SNAP_SERVER_NOAUTH=1`
* **Inference Server deployment:** Create app from Dockerfile `inference-server/Dockerfile` :
    * OCP example: `oc new-app --name inference-server https://itk-snap-dss:2EVH6Ky6zJPL7wn7QAsq@gitlab.com/PSLC/ia-medical/itk-snap-dss.git --context-dir inference-server`

## Running the service

In order to register services into to ITK-SNAP server, you need to provide a configuration file and to register a service provider. Configuration files are available in Github repositories to make things easier.

In the admin page of the running DSS server fill the following fields with the relevant information
* New provider : `IBM-LAB`
* New services assigned to `IBM-LAB` :
    * Provider: newly created provider (IBM-LAB)
    * Git repository (Lung segmentation configuration): https://github.com/sinitame/lung-segmentation-service
    * Git repository (Nodule detection configuration): https://github.com/sinitame/nodule-detection-service
    * Reference: leave blank

![](imgs/admin-screen-shot.png)

If everything is set up properly, you should now see your available services in the Services part of the Web Server available at <your-server-url> (ours is `http://itk.10.7.11.23.nip.io`).

![](imgs/services-screen-shot.png)