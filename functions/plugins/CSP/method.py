from mne.decoding import CSP

class PluginMethod(CSP):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.params = kwargs
