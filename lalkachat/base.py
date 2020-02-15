
class Base:
    def __init__(self, profiles, active_profile, config_prefix=None):
        self.prefix = config_prefix if config_prefix else self.__class__.__name__.lower()

        self.profiles = profiles
        self.active_profile_name = active_profile

    @property
    def class_configuration(self):
        return self.profiles.get(self.active_profile_name, {}).get(self.prefix, {})

    def save(self):
        raise NotImplementedError(f"Save should be implemented in {self.__class__.__name__}")


class Config:
    def save(self):
        raise NotImplementedError(f"Save should be implemented in {self.__class__.__name__}")
