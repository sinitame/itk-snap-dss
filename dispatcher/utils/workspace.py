
class Workspace(object):
    def __init__(self, workspace_file_path):
        self.file_path = workspace_file_path
        self.file_name = os.path.basename(workspace_file_path)
        self.workspace = minidom.parse(workspace_file)

    def add_segmentation(self, ticket_path, file_name):

        # Generate the filepath of segmentation from workspace path
        segmentation_file_path = self.find_file_path(file_name)

        # Create new entries in workspace XML
        IOHistory_node = self.create_IOHistory_node(segmentation_file_path)
        segmentation_layer_node = self.create_segmentation_layer_node(segmentation_file_path)

        # Insert new enties in workspace XML
        folders = original_workspace.getElementsByTagName("folder")
        for folder in folders:
            if folder.getAttribute("key") == "ProjectMetaData":
                folder.appendChild(IOHistory_node)
            elif folder.getAttribute("key") == "Layers":
                folder.appendChild(segmentation_layer_node)

        # Generate result file path
        result_workspace_file = os.path.join(ticket_path, "results", self.file_name)

        # Write new workspace file in result directory
        new_workspace = open(result_workspace_file,"w")
        self.workspace.writexml(new_workspace, encoding="UTF-8")
        new_workspace.close()

    def find_file_path(self, file_name):
        entries = self.workspace.getElementsByTagName("entry")
        for entry in entries:
            if entry.getAttribute("key") == "SaveLocation":
                file_path = entry.getAttribute("value")
                return file_path + '/' + file_name
        return ""

    def create_IOHistory_node(self, segmentation_file_path):

        # Create new node structure
        IOHistory_node = self.workspace.createElement("folder")
        IOHistory_node.setAttribute("key", "IOHistory")

        label_image_folder = self.workspace.createElement("folder")
        label_image_folder.setAttribute("key", "LabelImage")

        entry_1 = self.workspace.createElement("entry")
        entry_1.setAttribute("key", "ArraySize")
        entry_1.setAttribute("value", "1")
        label_image_folder.appendChild(entry_1)

        entry_2 = self.workspace.createElement("entry")
        entry_2.setAttribute("key", "Element[0]")
        entry_2.setAttribute("value", segmentation_file_path)
        label_image_folder.appendChild(entry_2)

        IOHistory_node.appendChild(label_image_folder)

        return IOHistory_node

    def create_segmentation_layer_node(self, segmentation_file_path):
        segmentation_layer_node = self.workspace.createElement("folder")
        segmentation_layer_node.setAttribute("key", "Layer[001]")

        entry_1 = self.workspace.createElement("entry")
        entry_1.setAttribute("key", "AbsolutePath")
        entry_1.setAttribute("value", segmentation_file_path)
        segmentation_layer_node.appendChild(entry_1)

        entry_2 = self.workspace.createElement("entry")
        entry_2.setAttribute("key", "Role")
        entry_2.setAttribute("value", "SegmentationRole")
        segmentation_layer_node.appendChild(entry_2)

        entry_3 = self.workspace.createElement("entry")
        entry_3.setAttribute("key", "Tags")
        entry_3.setAttribute("value", "")
        segmentation_layer_node.appendChild(entry_3)

        # Making IOHints folder node
        IOHints_folder = self.workspace.createElement("folder")
        IOHints_folder.setAttribute("key", "IOHints")

        entry_IOHints_folder = self.workspace.createElement("entry")
        entry_IOHints_folder.setAttribute("key", "Format")
        entry_IOHints_folder.setAttribute("value", "NRRD")
        IOHints_folder.appendChild(entry_IOHints_folder)

        segmentation_layer_node.appendChild(IOHints_folder)

        # Making layer metadata folder
        LayerMetaData_folder = self.workspace.createElement("folder")
        LayerMetaData_folder.setAttribute("key", "LayerMetaData")

        entry_LMD_1 = self.workspace.createElement("entry")
        entry_LMD_1.setAttribute("key", "Alpha")
        entry_LMD_1.setAttribute("value", "0")
        LayerMetaData_folder.appendChild(entry_LMD_1)

        entry_LMD_2 = self.workspace.createElement("entry")
        entry_LMD_2.setAttribute("key", "CustomNickName")
        entry_LMD_2.setAttribute("value", "")
        LayerMetaData_folder.appendChild(entry_LMD_2)

        entry_LMD_3 = self.workspace.createElement("entry")
        entry_LMD_3.setAttribute("key", "Sticky")
        entry_LMD_3.setAttribute("value", "1")
        LayerMetaData_folder.appendChild(entry_LMD_3)

        entry_LMD_4 = self.workspace.createElement("entry")
        entry_LMD_4.setAttribute("key", "Tags")
        entry_LMD_4.setAttribute("value", "")
        LayerMetaData_folder.appendChild(entry_LMD_4)

        segmentation_layer_node.appendChild(LayerMetaData_folder)

        return segmentation_layer_node


