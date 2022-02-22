from rest_framework import serializers
from rest_framework.fields import _UnvalidatedField
from rest_framework.utils import model_meta

from configuration.models import ConfigValue, Environment


class ConfigValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfigValue
        fields = ["id", "key", "value"]

    def build_property_field(self, field_name, model_class):
        """
        Create a read only field for model methods and properties.
        """
        if field_name != "value":
            return super().build_property_field(field_name, model_class)

        field_class = _UnvalidatedField
        field_kwargs = {}
        return field_class, field_kwargs


class EnvironmentSerializer(serializers.ModelSerializer):
    configuration = ConfigValueSerializer(many=True)

    class Meta:
        model = Environment
        fields = [
            "id",
            "name",
            "description",
            "propagate",
            "promotes_from",
            "configuration",
        ]

    def update(self, instance, validated_data):
        configuration = validated_data.pop("configuration", None)
        for config in configuration:
            ConfigValue.objects.update_or_create(
                environment=instance,
                key=config["key"],
                defaults={"value": config["value"]},
            )

        return super().update(instance, validated_data)
