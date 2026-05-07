from typing import Dict, Type

from macros.base_macro import BaseMacro
from macros.fishing_bomb_macro import FishingBombMacro
from macros.poison_farm_macro import PosionFarmMacro
# from macros.lock_macro import LockMacro
# from macros.poison_macro import PoisonMacro
# from macros.wine_macro import WineMacro
from macros.lock_farm_macro import LockFarmMacro

class MacroRegistry:
    def __init__(self):
        self.macros: Dict[str, Type[BaseMacro]] = {
            FishingBombMacro.id: FishingBombMacro,
            PosionFarmMacro.id: PosionFarmMacro,
            LockFarmMacro.id: LockFarmMacro
            # WineMacro.id: WineMacro,
            # LockMacro.id: LockMacro,
        }

    def get_macro_class(self, action: str) -> Type[BaseMacro]:
        macro_class = self.macros.get(action)

        if not macro_class:
            raise ValueError(f"未知宏 action：{action}")

        return macro_class