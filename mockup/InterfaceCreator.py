
class InterfaceCreator:
    def __init__ (self):
        raise NotImplementedError

    def get_project_name (self):
        raise NotImplementedError

    def get_project_description (self):
        raise NotImplementedError

    def get_druids (self):
        raise NotImplementedError

    def finish (self):
        raise NotImplementedError
