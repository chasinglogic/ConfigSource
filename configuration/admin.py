from django.contrib import admin

from configuration.models import ConfigValue, Environment


class EnvironmentAdmin(admin.ModelAdmin):
    pass


class ConfigValueAdmin(admin.ModelAdmin):
    pass


admin.site.register(Environment, EnvironmentAdmin)
admin.site.register(ConfigValue, ConfigValueAdmin)
