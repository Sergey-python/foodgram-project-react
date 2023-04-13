class UpdateMixin(object):
    """
    Миксин, предоставляющий метод update для отдельного объекта.
    """

    def update(self, **kwargs):
        if self._state.adding:
            raise self.DoesNotExist
        for field, value in kwargs.items():
            setattr(self, field, value)
        self.save(update_fields=kwargs.keys())
