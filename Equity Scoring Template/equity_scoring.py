import pandas as pd
from ipywidgets import HBox, VBox

from utils_general import format_floats, get_score_data, get_single_field_request
from utils_gui import ApplicationLogger, AppTitle, ComputeButton, DEFAULT_INITIALISATION_MSG, DEFAULT_WAITING_MSG, ParameterSelection, ScreeningDataGrid, WeightsBox, TotalScoreFilter



class EquityScoring(VBox):
    
    def __init__(self, factors, col_defs, connection, logger=None):
        self.factors = factors
        self.connection = connection
        if logger is None:
            logger = list()
        self.logger = logger
        self.parameter_selection = ParameterSelection()
        self.weights_box = WeightsBox(fields=factors.total_score_factors)
        self.top_bottom_filter = TotalScoreFilter()
        self.ctrl_button = ComputeButton(description='Update', on_click= lambda x: self.compute(), button_style='success', width=120)
        self.datagrid = ScreeningDataGrid(data = pd.DataFrame(), col_defs=col_defs)
        self.init_display = [self.parameter_selection, self.weights_box, self.top_bottom_filter, self.ctrl_button, DEFAULT_INITIALISATION_MSG, self.datagrid]
        super().__init__(children=self.init_display)
    
    @property
    def countries(self):
        return self.parameter_selection.regions[self.parameter_selection.region.value]
    
    @property
    def currency(self):
        return self.parameter_selection.currency.value
    
    @property
    def fields(self):
        fields = [f for factor in self.factors.factors for f in factor.fields.keys()]
        if len(self.factors.total_score_factors)>0:
            fields.insert(self.factors.total_score_position, 'Total Score')
        return fields
    
    @property
    def max_mktcap(self):
        return self.parameter_selection.max_mktcap.value
    
    @property
    def min_mktcap(self):
        return self.parameter_selection.min_mktcap.value
    
    @property
    def sector(self):
        return self.parameter_selection.sector.value
    
    @property
    def universe_ticker(self):
        return self.parameter_selection.universe.value
    
    @property
    def weights(self):
        return self.weights_box.weights
    
    @property
    def ref_date(self):
        return self.parameter_selection.as_of_date.value
    
    @property
    def rank_method(self):
        return self.top_bottom_filter.top_bottom.value
    
    @property
    def rank_num(self):
        return self.top_bottom_filter.num_stocks.value
    
    def compute(self):
        self.children = [self.parameter_selection, self.weights_box, self.top_bottom_filter, self.ctrl_button, DEFAULT_WAITING_MSG]
        self.update_data()
        self.datagrid.data = self.data.reset_index().rename(columns={'ID': 'Ticker'}).dropna()
        self.children = self.init_display
    
    def apply_as_of_date(self, fields, ref_date, apply_ref_date=False):
        if apply_ref_date:
            fld_keys = fields.keys()
            for fld in fld_keys:
                fields[fld] = fields[fld].as_of(ref_date)
        return fields
    
    def apply_match_screen_results(self, fields, screen_results):
        fld_keys = fields.keys()
        for fld in fld_keys:
            fields[fld] = self.connection.func.matches(fields[fld], self.connection.data.id().in_(screen_results))
        return fields
    
    def create_total_score_field(self):
        factor_in_use = [f for f in self.factors.factors if f.use_in_total_score]
        factor_in_use_field = []

        for f in factor_in_use:
            fields = self.apply_as_of_date(f.fields, self.ref_date, f.use_in_total_score)

            for k in fields:
                factor_in_use_field.append(fields[k])

        w = self.weights.divide(100).tolist()

        total_score_field = factor_in_use_field[0] * w[0]

        for i in range(1, len(w)):
            total_score_field = total_score_field + factor_in_use_field[i] * w[i]
        
        return total_score_field
    
    def create_total_score_screen(self, universe):
        total_score_field = self.create_total_score_field()
        
        if self.rank_method == 'Bottom':
            total_score_field = -1 * total_score_field
            
        return self.connection.univ.filter(universe, self.connection.func.grouprank(total_score_field) <= self.rank_num)
    
    
    def update_data(self):
        self.logger.append("Computing data with selected parameters")
        try:
            universe = self.connection.univ.members([self.universe_ticker], dates=self.ref_date)
            filter_mktcap = self.connection.func.between(
                self.connection.data.MARKET_CAP()/1000000, int(self.min_mktcap), int(self.max_mktcap))
            universe = self.connection.univ.filter(universe, filter_mktcap)
            
            if self.sector != 'All':
                filter_sector = self.connection.func.in_(self.connection.data.GICS_SECTOR_NAME(), [self.sector])
                universe = self.connection.univ.filter(universe, filter_sector)
            if self.countries is not None:
                filter_countries = self.connection.func.in_(self.connection.data.COUNTRY_FULL_NAME().toupper(), self.countries)
                universe = self.connection.univ.filter(universe, filter_countries)
            
            # screen with the total score
            screen = self.create_total_score_screen(universe)
            screen_results = get_single_field_request(
                connection=self.connection, universe=screen, field=self.connection.data.id(), field_name='ID', with_params={'currency': self.currency, 'fill': 'prev', 'mode': 'cached'}
            ).ID.tolist()
            
            data = pd.concat(
                [get_score_data(
                        connection=self.connection,
                        universe=universe,
                        fields=self.apply_match_screen_results(self.apply_as_of_date(factor.fields, self.ref_date, factor.use_in_total_score), screen_results),
                        with_params={'currency': self.currency, 'fill': 'prev', 'mode': 'cached'},
                        preferences={'SkipNa': factor.skipna_preference},
                    ).T
                for factor in self.factors.factors]
            ).T
            # Compute Total Score
            total_score_factors = self.factors.total_score_factors
            if len(total_score_factors) > 0:
                total_score = data[total_score_factors].multiply(self.weights.divide(100)).sum(axis=1).apply(format_floats).to_frame('Total Score')
                data = data.join(total_score).sort_values(by='Total Score', ascending=False)
            self.data = data
            self.logger.append('Finished Computing')
        except:
            self.logger.append('There was an ERROR during in the computations')


class EquityScoringApp(VBox):
    
    def __init__(self, factors, col_defs, connection, title, description=None):
        """
        Summary:
            A Container for the Asset Allocation App. The logger and the app are initialised here.
        Args:
            maps (dict): the dict of options available, mapped using names (key) and classes (value).
            fields (dict): the dict of fields available, mapped using names (key) and fields (value).
            connection (bq connection): a connection to the bql server initialised with bql.Service().
            title (str): the title of the app to be displayed on top in big characters.
            description (str): the description of the app to be displayed below the title in smaller characters.
        """
        self.title = title
        self.description = description
        self.logger = ApplicationLogger()
        self.app = EquityScoring(factors=factors, col_defs=col_defs, connection=connection, logger=self.logger)
        super().__init__(children=[AppTitle(title=self.title, description=description), self.app, self.logger])
    
