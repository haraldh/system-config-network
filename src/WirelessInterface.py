from InterfaceCreator import InterfaceCreator

class WirelessInterface (InterfaceCreator):
    def __init__ (self):
        pass

    def get_project_name (self):
        return "Wireless/wavelan card"

    def get_project_description (self):
        return "Create a new wireless connection.  This is a really lame description that should be fixed up later"

    def get_druid (self):
        pass

