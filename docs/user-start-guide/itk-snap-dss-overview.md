## ITK-SNAP

[ITK-SNAP](http://www.itksnap.org/pmwiki/pmwiki.php?n=Main.HomePage) is a free, open-source, and multi-platform software application used to segment structures in 3D medical images. It is the product of a decade-long collaboration between Paul Yushkevich, Ph.D., of the Penn Image Computing and Science Laboratory (PICSL) at the University of Pennsylvania, and Guido Gerig, Ph.D., of the Scientific Computing and Imaging Institute (SCI) at the University of Utah, whose vision was to create a tool that would be dedicated to a specific function, segmentation, and would be easy to use and learn.

You will find all the documentation available on ITK-SNAP [here](http://www.itksnap.org/pmwiki/pmwiki.php?n=Documentation.SNAP3).

## Distributed Segmentation Service

[Distributed Segmentation Services](https://alfabis-server.readthedocs.io/) (DSS) is a web-based platform for segmentation algorithm developers to make their tools available to ITK-SNAP users. DSS makes it possible to perform advanced and specialized segmentation tasks (such as machine learning based segmentation) on your data with minimal effort.

DSS is meant to connect developers of medical image analysis algorithms to their users. Users send images to the server, and algorithm providers download these images, process them, and upload the results for users to retrieve:

![ITK-SNAP DSS Architecture Overview](images/dss_arch.png)
