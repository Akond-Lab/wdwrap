#  Copyright (c) 2020. Mikolaj Kaluszynski et. al. CAMK, AkondLab
import json
import pandas as pd
import traitlets
from traitlets import observe, HasTraits
import ipyvuetify


class EnumSelect(ipyvuetify.Select):
    """ Class for comobobox on `traitlets.Enum`"""

    def __init__(self, obj: HasTraits, prop: str, **kwargs) -> None:
        self.trait = obj.class_traits()[prop]
        self.obj = obj
        self.prop = prop
        super().__init__(items=self.select_items(), v_model=getattr(obj, prop), **kwargs)

    def select_items(self):
        return [{'text': v, 'value': k} for k, v in self.trait.values.items()]

    @observe('v_model')
    def handler_v_model(self, change):
        setattr(self.obj, self.prop, change['new'])

class EnumSelect(ipyvuetify.Select):
    """ Class for comobobox on `traitlets.Enum`"""

    def __init__(self, obj: HasTraits, prop: str, **kwargs) -> None:
        self.trait = obj.class_traits()[prop]
        self.obj = obj
        self.prop = prop
        super().__init__(items=self.select_items(), v_model=getattr(obj, prop), **kwargs)

    def select_items(self):
        return [{'text': v, 'value': k} for k, v in self.trait.values.items()]

    @observe('v_model')
    def handler_v_model(self, change):
        setattr(self.obj, self.prop, change['new'])


class PandasDataFrame(ipyvuetify.VuetifyTemplate):
    """
    Vuetify DataTable rendering of a pandas DataFrame

    Taken directly from ipyvuetify examples

    Args:
        data (DataFrame) - the data to render
        title (str) - optional title
    """

    headers = traitlets.List([]).tag(sync=True, allow_null=True)
    items = traitlets.List([]).tag(sync=True, allow_null=True)
    search = traitlets.Unicode('').tag(sync=True)
    title = traitlets.Unicode('DataFrame').tag(sync=True)
    index_col = traitlets.Unicode('').tag(sync=True)
    template = traitlets.Unicode('''
        <template>
          <v-card>
            <v-data-table
                :headers="headers"
                :items="items"
                :item-key="index_col"
                :rows-per-page-items="[25, 50, 250, 500]"
            >
                <template v-slot:no-data>
                  <v-alert :value="true" color="yellow" icon="warning">
                    No data
                  </v-alert>
                </template>
                <template v-slot:no-results>
                    <v-alert :value="true" color="error" icon="warning">
                      Your search for "{{ search }}" found no results.
                    </v-alert>
                </template>
                <template v-slot:items="rows">
                  <td v-for="(element, label, index) in rows.item"
                      @click=cell_click(element)
                      >
                    {{ element }}
                  </td>
                </template>
            </v-data-table>
          </v-card>
        </template>
        ''').tag(sync=True)

    def __init__(self, *args,
                 data=pd.DataFrame(),
                 title=None,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self._data = data
        self.update()
        if title is not None:
            self.title = title

    def update(self):
        data = self._data.reset_index()
        self.index_col = data.columns[0]
        headers = [{
            "text": col,
            "value": col
        } for col in data.columns]
        headers[0].update({'align': 'left', 'sortable': True})
        self.headers = headers
        self.items = json.loads(
            data.to_json(orient='records'))

    def flush(self):
        self.df = pd.DataFrame()

    @property
    def df(self):
        return self._data

    @df.setter
    def df(self, dataframe):
        self._data = dataframe
        self.update()
