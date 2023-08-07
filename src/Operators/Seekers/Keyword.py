from src.Operators.OperatorBase import Operator


class Keyword(Operator):
    pass

    def __init__(self, input_query_values, k=10):
        Operator.__init__(self)
        self.type = 'intersection'
        self.input = set(input_query_values)
        self.k = k
        self.base_sql = ' $INIT$ ' + f'SELECT TableId FROM AllTables WHERE CellValue IN ($TOKENS$) $ADDITIONALS$ ' \
                        f'GROUP BY TableId ORDER BY COUNT(DISTINCT CellValue) DESC LIMIT $TOPK$' + ' $ENDING$ '

    def create_sql_query(self):
        self.sql = self.base_sql.replace('$TOKENS$', self.create_sql_where_condition_from_value_list(self.clean_value_collection(self.input)))\
            .replace('$TOPK$', f'{self.k}').replace('$ADDITIONALS$', '').replace('$INIT$', '(').replace('$ENDING$', ')')

    def optimize(self, by, set_operation_type, create_executatable_query=False): # by, is an operator that we would like to optimize the sql based on
        linear = False # If False means that the optimization merged the nodes and we don't need to linearly connect them together
        if set_operation_type == 'set_intersection':
            if by.type == 'intersection':
                by.create_sql_query()
                self.base_sql = self.base_sql.replace('$ADDITIONALS$', f' AND TableId IN ($PREVIOUSSTEP_MUST$) $ADDITIONALS$ ')
                linear = True
                self.k = min(self.k, by.k)
            elif by.type == 'multicolumnintersection' or by.type == 'quadrantapproximation':
                by.optimize(self, set_operation_type, True)
                self.base_sql = by.sql
        elif set_operation_type == 'set_counter':
            if by.type == 'intersection':
                by.create_sql_query()
                self.base_sql = self.base_sql.replace('$INIT$', f' $INIT$ ( ')
                self.base_sql = self.base_sql.replace('$ENDING$', f'  $ENDING$ ')
                self.base_sql = self.base_sql.replace('$INIT$', f' $INIT$ {by.sql})  UNION ALL ')
            elif by.type == 'multicolumnintersection' or by.type == 'quadrantapproximation':
                by.optimize(self, set_operation_type, True) # this might need to change. base SQL doesn't contain all sql code needed
                self.base_sql = by.sql
        elif set_operation_type == 'set_union':
            if by.type == 'intersection':
                # by.create_sql_query()
                self.base_sql = self.base_sql.replace('$INIT$', f' $INIT$ ( ')
                self.base_sql = self.base_sql.replace('$ENDING$', f'  ) $ENDING$ ')
                self.base_sql = self.base_sql.replace('$INIT$', f' $INIT$ ({by.sql}) UNION DISTINCT ')
                self.k = self.k + by.k
            elif by.type == 'multicolumnintersection' or by.type == 'quadrantapproximation':
                by.optimize(self, set_operation_type, True) # this might need to change. base SQL doesn't contain all sql code needed
                self.base_sql = by.sql
        elif set_operation_type == 'set_difference':
            if by.type == 'intersection':
                self.input = set(self.input).difference(set(by.input))
            elif by.type == 'multicolumnintersection' or by.type == 'quadrantapproximation':
                by.create_sql_query()
                self.base_sql = self.base_sql.replace('$ADDITIONALS$', f' AND TableId NOT IN ({by.sql}) $ADDITIONALS$ ')
        if create_executatable_query:
            self.create_sql_query()
        return linear

