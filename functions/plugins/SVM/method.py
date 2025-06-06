from sklearn.svm import SVC

class PluginMethod(SVC):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.params = kwargs
