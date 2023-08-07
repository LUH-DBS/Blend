class Operator(object):
    def __init__(self):
        self.type = ''
        self.sql = ''
        self.base_sql = ''

    def clean_value_collection(self, values):
        return [str(v).replace("'", "''").strip() for v in values if str(v).lower() != 'nan']

    def create_sql_where_condition_from_value_list(self, values):
        return "'{}'".format("' , '".join(set(values)))

    def create_sql_where_condition_from_numerical_value_list(self, values):
        values = [str(x) for x in values]
        return "{}".format(" , ".join(values))