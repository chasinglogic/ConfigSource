from configuration.models import ConfigValue, Environment
from django.test import TestCase


class TestValueResolution(TestCase):
    def test_single_environment(self):
        env = Environment.objects.create(name="production")
        env.configuration.create(key="DB_HOST", value="localhost")
        env.configuration.create(key="DB_USER", value="user")
        env.configuration.create(key="DB_PASS", value="pass")

        self.assertEqual(env.get_value("DB_HOST"), "localhost")
        self.assertEqual(env.get_value("DB_USER"), "user")
        self.assertEqual(env.get_value("DB_PASS"), "pass")

    def test_environment_raises_keyerror(self):
        env = Environment.objects.create(name="production")
        env.configuration.create(key="DB_HOST", value="localhost")
        env.configuration.create(key="DB_USER", value="user")
        env.configuration.create(key="DB_PASS", value="pass")

        with self.assertRaises(KeyError):
            env.get_value("INVALID")

    def test_higher_propagates_to_lower(self):
        env = Environment.objects.create(name="production", propagate=True)
        env.configuration.create(key="DB_HOST", value="localhost")
        env.configuration.create(key="DB_USER", value="user")
        env.configuration.create(key="DB_PASS", value="pass")

        staging = Environment.objects.create(name="staging")
        env.promotes_from = staging
        env.save()

        self.assertEqual(staging.get_value("DB_HOST"), "localhost")
        self.assertEqual(staging.get_value("DB_USER"), "user")
        self.assertEqual(staging.get_value("DB_PASS"), "pass")
