from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers


class BaseSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        instance = self.instance or self.Meta.model()
        for name, value in attrs.items():
            if not self.Meta.model._meta.get_field(name).many_to_many:
                setattr(instance, name, value)
        try:
            instance.full_clean(exclude=[f.name for f in self.Meta.model._meta.many_to_many])
        except DjangoValidationError as exc:
            raise serializers.ValidationError(getattr(exc, "message_dict", exc.messages)) from exc
        return attrs

    class Meta:
        fields = "__all__"


def serializer_for(model):
    audit_fields = ("created_by", "created_at", "updated_by", "updated_at")
    model_fields = {field.name for field in model._meta.get_fields()}
    return type(
        f"{model.__name__}Serializer",
        (BaseSerializer,),
        {
            "Meta": type(
                "Meta",
                (),
                {
                    "model": model,
                    "fields": "__all__",
                    "read_only_fields": tuple(field for field in audit_fields if field in model_fields),
                },
            )
        },
    )
