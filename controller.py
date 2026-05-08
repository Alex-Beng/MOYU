"""状态机主循环"""
import time
from vision.detector import Detector
from device.scrcpy_client import ScrcpyClient
from device.cube_api import CubeAPI
from recipe.loader import RecipeLoader


class Controller:
    """主控制器"""

    def __init__(self):
        self.recipe = RecipeLoader()
        self.detector = Detector()
        self.scrcpy = ScrcpyClient()
        self.cube = CubeAPI()
        self.state = "wait_init"

    def run(self):
        """主循环"""
        while True:
            if self.state == "wait_init":
                self._handle_wait_init()
            elif self.state == "init":
                self._handle_init()
            elif self.state == "scramble":
                self._handle_scramble()
            elif self.state == "solve":
                self._handle_solve()
            elif self.state == "reinit":
                self._handle_reinit()
            time.sleep(0.1)

    def _handle_wait_init(self):
        pass

    def _handle_init(self):
        pass

    def _handle_scramble(self):
        pass

    def _handle_solve(self):
        pass

    def _handle_reinit(self):
        pass


def main():
    controller = Controller()
    controller.run()
