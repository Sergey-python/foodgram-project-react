class FilterClass:
    def get_filter_field(self, key) -> str:
        return getattr(self, key).filter_field

    def get_filter_values(self, key, values) -> list:
        return list(map(getattr(self, key).convert_value, values.split(",")))

    def get_filter_fields(self, query_params):
        return {
            self.get_filter_field(key): set(
                map(
                    getattr(self, key).convert_value, query_params.getlist(key)
                )
            )
            for key in query_params
            if key in self.Meta.fields
        }


class FilterField:
    def __init__(self, filter_field):
        self.filter_field = filter_field

    @staticmethod
    def conver_value(value):
        raise NotImplementedError


class IntegerFilterField(FilterField):
    value_type = int

    @staticmethod
    def convert_value(value):
        return int(value)


class StringFilterField(FilterField):
    value_type = str

    @staticmethod
    def convert_value(value):
        return value


class BooleanFilterField(FilterField):
    value_type = bool

    @staticmethod
    def convert_value(value):
        return bool(int(value))
