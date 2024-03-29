"""mcpython - a minecraft clone written in python licenced under MIT-licence
authors: uuk, xkcdjerry

original game by forgleman licenced under MIT-licence
minecraft by Mojang

blocks based on 1.14.4.jar of minecraft, downloaded on 20th of July, 2019"""
import globals as G
import event.EventBus
import event.EventHandler
import traceback


class ModDependency:
    def __init__(self, name: str, versions=None):
        """
        creates an new mod dependency instance. need to be assigned with another mod
        :param name: the name of the mod
        :param versions: None if all, version if only one, list of versions if only a group,
                         list of False and than versions for not (excluding)

        """
        self.name = name
        self.versions = versions

    def arrival(self) -> bool:
        if self.name not in G.modloader.mods: return False
        if self.versions is None: return True
        real_mod = G.modloader[self.name]
        if self.versions == real_mod.version: return True
        if type(self.versions) == list:
            if real_mod.version in self.versions: return bool(real_mod[0])
        return False

    def get_version(self):
        return G.modloader.mods[self.name].version

    def get_loading_stage(self):
        pass

    def __str__(self):
        if not self.versions:
            return self.name
        elif type(self.versions) == str:
            if self.versions[0]:
                return "{} in any of the following versions: ".format(self.name) + ", ".join(self.versions)
            else:
                return "{} in none any of the following versions: ".format(self.name) + ", ".join(self.versions[1:])
        else:
            return "{} in version {}".format(self.name, self.versions)


class Mod:
    """
    class for mods. for creating an new mod, create an instance of this
    """

    def __init__(self, name: str, version):
        """
        creates an new mod
        :param name: the name of the mod
        """
        self.name = name
        self.eventbus: event.EventBus.EventBus = event.EventHandler.LOADING_EVENT_BUS.create_sub_bus()
        self.dependinfo = [[] for _ in range(5)]  # need, possible, not possible, before, after
        self.path = None
        self.version = version
        G.modloader.add_to_add(self)

    def add_dependency(self, depend):
        self.dependinfo[0].append(depend)
        self.dependinfo[4].append(depend)

    def add_not_load_dependency(self, depend):
        self.dependinfo[0].append(depend)

    def add_not_compatible(self, depend):
        self.dependinfo[2].append(depend)

    def add_load_before_if_arrival(self, depend):
        self.dependinfo[1].append(depend)
        self.dependinfo[3].append(depend)

    def add_load_after_if_arrival(self, depend):
        self.dependinfo[1].append(depend)
        self.dependinfo[4].append(depend)

