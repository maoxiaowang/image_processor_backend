

class UpdateMixin:
    update_serializer_class = None

    def get_serializer_class(self):
        if self.request.method == 'PUT':
            return self.update_serializer_class or self.serializer_class
        return super().get_serializer_class()


class CreateMixin:
    create_serializer_class = None

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return self.create_serializer_class or self.serializer_class
        return super().get_serializer_class()
