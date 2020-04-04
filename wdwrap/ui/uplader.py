#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import ipywidgets as widgets
import pandas as pd

class Uploader(object):

    def __init__(self, title, icon='upload', accept='') -> None:
        super().__init__()
        self.widget = widgets.FileUpload(description=title, icon=icon, accept=accept, multiple=False)

    def content(self):
        if len(self.widget.value) == 0:
            return None
        try:  # widgets 8
            [uploaded_file] = self.widget.value
            return uploaded_file['content'].to_bytes()
        except TypeError:
            return list(self.widget.value.values())[0]['content']

        except ValueError:  # nothing uploaded
            return None

    def filename(self):
        if len(self.widget.value) == 0:
            return None
        try:  # widgets 8
            [uploaded_file] = self.widget.value
            return uploaded_file['name']
        except TypeError:
            return list(self.widget.value.values())[0]['metadata']['name']

        except ValueError:  # nothing uploaded
            return None


    def fd(self):
        """File descriptor open to read content of uploaded file"""
        from io import BytesIO
        return BytesIO(self.content())




class LcUploader(Uploader):

    def __init__(self, title='Observed LC', icon='plus', accept='') -> None:
        super().__init__(title, icon, accept)
        # self._df = None
        #
        # def hook(change):
        #     self._df = None
        # self.widget.observe(hook, 'value')

    def to_dataframe(self):
        """Pandas DataFrame ready to use"""
        return pd.read_table(self.fd(), index_col=0, usecols=[0, 1], delim_whitespace=True,
                             names=['hjd', 'mag'])

class RvUploader(Uploader):

    def __init__(self, title='Observed RV', icon='plus', accept='') -> None:
        super().__init__(title, icon, accept)

    def to_dataframe(self):
        """Pandas DataFrame ready to use"""
        return pd.read_table(self.fd(), index_col=0, usecols=[0, 1, 2, 3, 4, 5], delim_whitespace=True,
                             names=['hjd', 'rv1', 'rv1_e', 'rv2', 'rv2_e', 'instr'])
