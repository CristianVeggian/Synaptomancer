from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

class PluginMethod(LinearDiscriminantAnalysis):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.params = kwargs
