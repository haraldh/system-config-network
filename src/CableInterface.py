from InterfaceCreator import InterfaceCreator

class CableInterface (InterfaceCreator):
    def __init__ (self):
        pass

    def get_project_name (self):
        return "Cable modem"

    def get_project_description (self):
        return "Create a new cable modem connection.  The dialup interface is used primarily for connecting to an ISP over a cable modem.  This is a really lame description that should be fixed up later"

    def get_druid (self):
        pass

