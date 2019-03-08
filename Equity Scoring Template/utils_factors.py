import numpy as np
from collections import OrderedDict


class BQLFunction(object):
    
    def __init__(self, name, bql_function, sign=None, relative_weight=None):
        '''
        Summary:
            A class to store information about a BQL function.
        
        Args:
            name (str): name of the function.
            bql_function (BQL item): the BQL function to be used.
            sign (float): +1 or -1, depending on whether the function is positive or negative 
                for the score. Defaults to 1.
            relative_weight (float): a weight greater or equal to zero; this corresponds
                to how much the function will contribute to the score. Defaults to 1.
        '''
        
        self.name = name
        self.bql_function = bql_function
        if sign is None:
            sign = 1.
        self.sign = np.sign(sign)
        if relative_weight is None:
            relative_weight = 1.
        self.relative_weight = max(relative_weight, 0) # can't be negative
    
    @property
    def summary(self):
        ''' Returns a tuple with the name and the bql_function'''
        return (self.name, self.bql_function)
    
    @property
    def signed_function(self):
        ''' Returns the bql_function prepared to be summed to other functions
        within the group, i.e. multiplied by its sign and '''
        return self.sign * self.bql_function
    

class Factor(object):
    
    def __init__(self, name, bql_functions=None, skipna_preference=True, use_in_total_score=False):
        ''' 
        Summary:
            A general collector of FactorFunctions that is handy for adding new FactorFunctions.
        Args:
            name (str): the name of the collector - very useful when functions are aggregated.
            bql_functions (collection): a collection of BQLFunction elements.
            skipna_preference (bool): will or will not skipna when retrieving the data.
        '''
        self.name = name
        if bql_functions is not None:
            self.bql_functions = bql_functions
        else:
            self.bql_functions = []
        self.skipna_preference = skipna_preference
        self.use_in_total_score = use_in_total_score
    
    def add_bql_function(self, bql_function):
        ''' Append a BQLFunction element.'''
        self.bql_functions.append(bql_function)
    
    def add_factor(self, name, bql_function, sign=None, relative_weight=None):
        ''' Add a BQLFunction element with given name, bql_function, sign and relative_weight.'''
        
        self.add_bql_function(BQLFunction(name, bql_function, sign, relative_weight))
    
    @property
    def sum_relative_weights(self):
        ''' Will sum the relative_weights of all BQLFunctions in the object.'''
        return sum([bf.relative_weight for bf in self.bql_functions])
    
    @property
    def sum_squared_relative_weights(self):
        ''' Will sum the relative_weights of all BQLFunctions in the object.'''
        return sum([bf.relative_weight**2 for bf in self.bql_functions])
    
    @property
    def original_fields(self):
        ''' Displays all functions listed.'''
        return OrderedDict([bf.summary for bf in self.bql_functions])
    
    @property
    def fields(self):
        ''' Method implemented in the subclasses. This is only a general class.'''
        raise Error("Not implemented yet")


class DescriptiveFactor(Factor):
    '''
    Inherits from Factors: a collector of BQLFunctions.
    The class will display all the functions, without any manipulation.
    The method used to display the fields is 'fields'.
    '''
    
    def __init__(self, name, bql_functions=None, skipna_preference=True, use_in_total_score=False):
        super().__init__(name, bql_functions, skipna_preference=skipna_preference, use_in_total_score=use_in_total_score)
    
    @property
    def fields(self):
        ''' Displays all functions listed.'''
        return self.original_fields
    

class RankedFactor(Factor):
    '''
    Inherits from Factors: a collector of BQLFunctions.
    The class will rank the functions, and will then display the weighted average rank.
    The method used to display the fields is 'fields'.
    '''
    
    def __init__(self, name, bql_functions=None, skipna_preference=False, use_in_total_score=True):
        super().__init__(name, bql_functions, skipna_preference=skipna_preference, use_in_total_score=use_in_total_score)
    
    @property
    def fields(self):
        ''' Displays the weighted average of the rankings.'''
        rankings = [bf.relative_weight * bf.signed_function.group().rank(ties='max').ungroup() for bf in self.bql_functions]
        average = sum(rankings) / self.sum_relative_weights
        return OrderedDict([(self.name, average)])
    

class ZScoreFactor(Factor):
    '''
    Inherits from Factors: a collector of BQLFunctions of the BQLFunctions.
    The class will compute the z-score of the functions, and will then display the weighted average z-score.
    The method used to display the fields is 'fields'.
    '''
    
    def __init__(self, name, bql_functions=None, fillna_value=-3, skipna_preference=True, use_in_total_score=True):
        super().__init__(name, bql_functions, skipna_preference=skipna_preference, use_in_total_score=use_in_total_score)
        self.fillna_value = fillna_value
    
    @property
    def fields(self):
        ''' Displays the weighted average of the zscores of the BQLFunctions.'''
        zscores = [bf.relative_weight * bf.signed_function.groupzscore().replacenonnumeric(self.fillna_value) for bf in self.bql_functions]
        average = sum(zscores) / self.sum_relative_weights
        average = sum(zscores) / (self.sum_squared_relative_weights ** 0.5)
        return OrderedDict([(self.name, average)])
    

class AllFactors(object):
    
    def __init__(self, factors=None, total_score_position=0):
        ''' 
        Summary:
            A general collector of Factor objects that is used to compute the total score.
        Args:
            factors (collection): a collection of Factor objects.
            total_score_position (int): the position where the Total Score should be (defaults to 0).
        '''
        if factors is not None:
            self.factors = factors
        else:
            self.factors = []
        self.total_score_position = total_score_position
    
    def append(self, factor):
        self.factors.append(factor)
    
    @property
    def total_score_factors(self):
        return [factor.name for factor in self.factors if factor.use_in_total_score==True]
    
