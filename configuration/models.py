import logging

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
logger = logging.getLogger(__name__)


class Environment(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    propagate = models.BooleanField(
        default=False,
        help_text="If set then this environment will propagate it's configuration values down to lower environments",
    )
    promotes_from = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="promotes_to",
    )

    def __str__(self):
        return self.name

    def get_value(self, key):
        try:
            config = self.configuration.get(key=key)
            return config.value
        except Exception as exc:
            higher_env = self.promotes_to.filter()
            if higher_env:
                return higher_env[0].get_value(key)

            raise KeyError(f"Key {key} not found in environment {self.name}")

    @property
    def configuration(self):
        logger.debug("Getting configuration for environment %s", self.name)
        values = list(self.configuration_values.all())
        higher_env = self.promotes_to.get() if self.promotes_to.exists() else None
        while higher_env:
            logger.debug("Found higher env %s collecting values...")
            if higher_env.propagate:
                lower_precedence_values = higher_env.configuration_values.exclude(
                    key__in=[v.key for v in values],
                )
                values.extend(lower_precedence_values)

            higher_env = (
                higher_env.promotes_to.get()
                if higher_env.promotes_to.exists()
                else None
            )

        return values


class ConfigValueManager(models.Manager):
    def type_value(self, kwargs):
        if "value" in kwargs:
            value = kwargs.pop("value")
            if isinstance(value, int):
                kwargs["int_value"] = value
            elif isinstance(value, float):
                kwargs["float_value"] = value
            elif isinstance(value, bool):
                kwargs["bool_value"] = value
            elif isinstance(value, str):
                kwargs["str_value"] = value

        return kwargs

    def create(self, **kwargs):
        self.type_value(kwargs)
        super().create(**kwargs)

    def update(self, **kwargs):
        self.type_value(kwargs)
        super().update(**kwargs)

    def update_or_create(self, defaults=None, **kwargs):
        self.type_value(kwargs)
        if defaults:
            self.type_value(defaults)
        return super().update_or_create(defaults=defaults, **kwargs)


class ConfigValue(models.Model):
    objects = ConfigValueManager()

    environment = models.ForeignKey(
        Environment, on_delete=models.CASCADE, related_name="configuration_values"
    )
    key = models.CharField(max_length=255)

    # TODO: Maybe don't need since the type is erased / converted to Float by JSON?
    int_value = models.IntegerField(blank=True, null=True)

    str_value = models.TextField(blank=True, null=True)
    float_value = models.FloatField(blank=True, null=True)
    bool_value = models.BooleanField(blank=True, null=True)

    class Meta:
        unique_together = ("environment", "key")

    def __str__(self):
        return f"ConfigValue({self.key}, {self.value})"

    @property
    def value(self):
        if self.int_value is not None:
            return self.int_value

        if self.str_value is not None:
            return self.str_value

        if self.float_value is not None:
            return self.float_value

        if self.bool_value is not None:
            return self.bool_value
        return self.key
