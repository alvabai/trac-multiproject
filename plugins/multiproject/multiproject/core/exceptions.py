class SingletonExistsException(Exception):
    def __init__(self, value=''):
        self.value = "Don't create singletons through constructor!\n" + value

    def __str__(self):
        return repr(self.value)

class ProjectValidationException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
