from abc import ABC, abstractmethod
from dataclasses import dataclass
from operator import itemgetter


@dataclass
class Engine(ABC):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def disconnect(self):
        pass

    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def observe(self):
        pass

    @abstractmethod
    def actions(self):
        pass

    @abstractmethod
    def play(self, action):
        pass

    @abstractmethod
    def result(self):
        pass


@dataclass
class WrapperEngine(Engine, ABC):
    engine: Engine

    def connect(self):
        return self.engine.connect()

    def disconnect(self):
        return self.engine.disconnect()

    def reset(self):
        return self.engine.reset()

    def observe(self):
        return self.engine.observe()

    def actions(self):
        return self.engine.actions()

    def play(self, action):
        return self.engine.play(action)

    def result(self):
        return self.engine.result()


@dataclass
class WorstEngine(WrapperEngine):
    def actions(self):
        actions = super().actions()

        actions.sort(key=itemgetter(1))

        return actions
