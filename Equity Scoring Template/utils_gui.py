from collections import deque, OrderedDict
from ipywidgets import HTML, Layout, Dropdown, Button, VBox, HBox, BoundedFloatText, BoundedIntText, Label, Text
import pandas as pd

from bqwidgets import DataGrid
from bqwidgets import DatePicker


DEFAULT_WAITING_MSG = HTML(
    value="""<p>Updating. Please Wait...</p>
    <i class="fa fa-spinner fa-spin fa-2x fa-fw" style="color:white;"></i>""",
    layout=Layout(margin='25px 0 10px 5px'))

DEFAULT_INITIALISATION_MSG = HTML(value='<p>Click on the "Update" button to run the query with the selected values</p>',
    layout=Layout(margin='25px 0 10px 5px'))


# Grid

class Grid(object):
    ''' The class automatically closes Datagrid when reloaded
    and additionally display the Datagrid in a box. '''
    
    def __init__(self):
        # Initialize the chart with default ticker
        self.data_grid = DataGrid(data=[], layout=Layout(display='none',  flex='1'))
        self.box = HBox([self.data_grid])
        
    def close(self):
        self.data_grid.close()
        self.box.close()
    
    def show(self):
        return self.box
    
    def populate_data(self, data):
        self.close()
        self.data_grid = DataGrid(data=data, layout=Layout(height='500px', flex='1'))
        self.box = HBox([self.data_grid])
    

class ScreeningDataGrid(DataGrid):
    ''' The Table where all the computations are shown.'''
    
    # Define the output table column definitions
    def __init__(self, data, col_defs):
        col_defs = [{'width': 150, 'filter': 'text',   'field': 'Ticker', 'headerName': 'Ticker', 'pinned': 'left', 'headerStyle': {'text-align': 'center'}}] + col_defs
        #            [{'width': len(field)*7+45, 'filter': 'number', 'field': field, 'headerName': field, 'headerStyle': {'text-align': 'center'}} for field in fields]
        # grid_options = {'rowSelection': 'single', 'enableColResize': True, 'enableFilter': True, 'enableSorting': True}
        super().__init__(data=data, column_defs=col_defs, layout=Layout(flex='1', height='300px', margin='10px 0 10px 0'))
        
        
# Buttons

class ComputeButton(Button):
    ''' Standard, big Compute button from Button.'''
    
    def __init__(self, width=100, button_style='primary', *args, **kwargs):
        layout = kwargs.pop('layout', Layout(width='{w}px'.format(w=str(width))))
        description = kwargs.pop('description', "COMPUTE")
        tooltip = kwargs.pop('tooltip', "Compute Allocations")
        super().__init__(layout=layout, description=description, tooltip=tooltip, button_style=button_style, *args, **kwargs)
        on_click = kwargs.get('on_click', None)
        if on_click is not None:
            self.on_click(on_click)


# Selection of Parameter

class DropdownAndLabel(VBox):
    
    def __init__(self, options, label, width, value=None):
        '''
        Summary:
            A Dropdown with a label on top.
        Args:
            options (dict): the dict of options available in the dropdown mapped by names (keys) and values.
            label (str): the label on top of the dropdown.
            width (int): the width of the dropdown and the label.
            value (obj): the initial value.
        '''
        self.label = Label(value=label, layout=Layout(width='{w}px'.format(w=width)))
        if value is None:
            self.dd = Dropdown(options=options, layout=Layout(width='{w}px'.format(w=width)))
        else:
            self.dd = Dropdown(options=options, value=value, layout=Layout(width='{w}px'.format(w=width)))
        super().__init__(children=[self.label, self.dd], layout=Layout(margin='0 0 10px 0'))
        
    @property
    def value(self):
        ''' Returns the value selected from the dropdown.'''
        return self.dd.value
    
    @property
    def key(self):
        ''' Returns the key selected from the dropdown.'''
        return [k for k,v in self.dd.options.items() if v==self.value][0]
    

class MonthDropDown(DropdownAndLabel):
    
    def __init__(self, width, label='Month', value=None):
        ''' Inherits from DropdownAndLabel. The options are a dictionary of months mapped to their numbers.'''
        options = OrderedDict([
            ('Jan', 1),
            ('Feb', 2),
            ('Mar', 3),
            ('Apr', 4),
            ('May', 5),
            ('Jun', 6),
            ('Jul', 7),
            ('Aug', 8),
            ('Sep', 9),
            ('Oct', 10),
            ('Nov', 11),
            ('Dec', 12),
        ])
        super().__init__(options, label, width, value)
    

class IntBoxAndLabel(VBox):
    
    def __init__(self, label, width, init_value=0, min_value=0, max_value=100):
        '''
        Summary:
            A slider with a label on top. Only integers allowed in the slider.
        Args:
            label (str): the label on top of the slider.
            width (int): the width of the slider and the label.
            init_value (int): the initial value in the slider.
            min_value (int): the minimum value in the slider.
            max_value (int): the maximum value in the slider.
        '''
        self.label = Label(value=label, layout=Layout(width='{w}px'.format(w=width)))
        self.bi = BoundedIntText(value=init_value, min=min_value, max=max_value, layout=Layout(width='{w}px'.format(w=width)))
        super().__init__(children=[self.label, self.bi], layout=Layout(margin='0 0 10px 0'))
        
    @property
    def value(self):
        ''' Returns the value selected from the slider.'''
        return self.bi.value
    

class TextBoxAndLabel(VBox):
    
    def __init__(self, label, width, value='INDU Index'):
        '''
        Summary:
            A text box with a label on top.
        Args:
            label (str): the label on top of the text box.
            width (int): the width of the text box and the label.
            init_value (str): the initial value in the text box.
        '''
        self.label = Label(value=label, layout=Layout(width='{w}px'.format(w=width)))
        self.text = Text(value=value, layout=Layout(width='{w}px'.format(w=width)))
        super().__init__(children=[self.label, self.text], layout=Layout(margin='0 0 10px 0'))
        
    @property
    def value(self):
        ''' Returns the value selected from the slider.'''
        return self.text.value
    

class DatePickerAndLabel(VBox):
    
    def __init__(self, label, width, value=None):
        '''
        Summary:
            A DatePicker with a label on top.
        Args:
            label (str): the label on top of the dropdown.
            width (int): the width of the date picker and the label.
            value (str): the initial value.
        '''
        self.label = Label(value=label, layout=Layout(width='{w}px'.format(w=width)))
        if value is None:
            value = str(pd.datetime.today().date())
        self.dp = DatePicker(value=value, date_format='%Y-%m-%d', layout=Layout(width='{w}px'.format(w=width)))
        super().__init__(children=[self.label, self.dp], layout=Layout(margin='0 0 10px 0'))
        
    @property
    def value(self):
        ''' Returns the value selected from the dropdown.'''
        return self.dp.value
    
#     @property
#     def key(self):
#         return [k for k,v in self.dd.options.items() if v==self.value][0]


class ParameterSelection(VBox):
    
    def __init__(self):
        # Sectors and Regions
        self.sectors_available = [
            'Communication Services', 'Consumer Discretionary', 'Consumer Staples', 'Energy', 'Financials', 
            'Health Care', 'Industrials', 'Information Technology', 'Materials', 'Real Estate', 'Utilities'
        ]
        
        self.regions = OrderedDict([('All', None)] + [(name, df.dropna().values.tolist()) for name, df in pd.read_csv('regions_mapping.csv').items()])
        # Elements
        self.universe = TextBoxAndLabel(label='Universe', value='SX5E Index', width=120)
        self.as_of_date = DatePickerAndLabel(label='Ref Date', width=120)
        self.sector = DropdownAndLabel(label='Sector Filter', options=['All'] + self.sectors_available, value='All', width=200)
        self.region = DropdownAndLabel(label='Region Filter', options=self.regions.keys(), value='All', width=200)
        self.currency = DropdownAndLabel(label='Currency', options=['EUR', 'GBP', 'CHF', 'USD', 'SKK', 'NOK', 'DKK'], value='EUR', width=120)
        self.min_mktcap = IntBoxAndLabel(label='Min Mkt Cap (M)', init_value=0, min_value=0, max_value=10000000, width=120)
        self.max_mktcap = IntBoxAndLabel(label='Max Mkt Cap (M)', init_value=10000000, min_value=0, max_value=10000000, width=120)
        
        # Initialisation
        univ_form = HBox([
            self.universe,
            self.as_of_date,
            self.region,
            self.sector,
        ])
        
        mkt_cap_form = HBox([
            self.currency,
            self.min_mktcap,
            self.max_mktcap,
        ])
        
        children = [
            univ_form,
            mkt_cap_form
        ]
        
        super().__init__(children=children, layout=Layout(margin='0 0 10px 0'))


# Weights

class WeightFloat(HBox):
    
    def __init__(self, name, init_value, max_value=100):
        self.label = Label(value=name,  layout=Layout(width='120px'))
        self.float_text = BoundedFloatText(min=0, max=max_value, value=init_value, layout=Layout(width='120px'))
        super().__init__(children=[self.label, self.float_text])
    

class WeightsBox(VBox):
    
    def __init__(self, fields, max_value=100):
        self.max_value = max_value
        self.boxes = OrderedDict()
        for field in fields:
            slider_box = WeightFloat(name=field, init_value=self.max_value/len(fields), max_value=self.max_value)
            self.boxes[field] = slider_box
        self.sum_100_button = ComputeButton(description='Sum to 100', on_click=lambda x: self.sum_100(), width=120)
        self.equalise_weights_button = ComputeButton(description='Equalise', on_click=lambda x: self.equalise_weights(), width=120)
        super().__init__(children=[Label(value='Factor Weights',  layout=Layout(width='200px'))] + [v for v in self.boxes.values()]+[HBox([self.sum_100_button,self.equalise_weights_button])])
    
    @property
    def weights(self):
        return pd.Series({name: box.float_text.value for name,box in self.boxes.items()})
    
    def sum_100(self):
        total_weights = self.weights.sum()
        ratio = self.max_value / total_weights
        for box in self.boxes.values():
            box.float_text.value *= ratio

    def equalise_weights(self):
        for box in self.boxes.values():
            box.float_text.value = self.max_value/len(self.boxes)


# Total Score Filter
class TotalScoreFilter(HBox):
    
    def __init__(self):
        self.top_bottom = DropdownAndLabel(label='Top/Bottom', options=['Top', 'Bottom'], value='Top', width=120)
        self.num_stocks = DropdownAndLabel(label='Num. Stocks', options=[10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 300], value=50, width=120)
        
        super().__init__(children=[self.top_bottom, self.num_stocks], layout=Layout(margin='20px 0 0 0'))
            
            
# Title

class AppTitle(HTML):
    
    def __init__(self, title, description=None, *args, **kwargs):
        ''' Standard title and description from HTML.'''
        value = '<h2 style="color: lightgrey; font-weight: bold;">{text}</h2>'.format(text=title)
        if description is not None:
            description = '<h4 style="color: lightgrey">{text}</h4>'.format(text=description)
            value = "".join([value, description])
        super().__init__(value=value, *args, **kwargs)
        self.layout.margin = '0px 0px 15px 0px'
    


# Logger

class ApplicationLogger(HTML):
    
    def __init__(self, max_msgs=20, *args, **kwargs):
        ''' Application logger from HTML. Displays max max_msgs logs.'''
        # Initialisation
        self.layout = Layout(display='flex', max_height='75px', min_height='25px', overflow_y='auto', border='2px solid white')
        self.msg_queue = deque(maxlen=max_msgs)
        super().__init__(value='', layout=self.layout, *args, **kwargs)

    def append(self, msg, color='limegreen'):
        ''' Adds a message to the logger. The message will have date and time.'''
        msg = """<font color="{font_color}">{msg}</font>""".format(font_color=str(color), msg=msg)
        timestamp = pd.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        modified_msg = "%s - %s" % (timestamp, msg)
        self.msg_queue.appendleft(modified_msg)
        self.show()

    def show(self):
        ''' Displays the object. The value is inherited from HTML. Updating/initialising it with elements displays the elements.'''
        html_string = "\n<br>".join(list(self.msg_queue))
        self.value = html_string
