from iconservice import *
import os

TAG = 'LayerXToken'
SYMBOL = 'LXT'


class TokenStandard(ABC):
    """
    IRC2 token standard's interface
    Ref)1. https://github.com/sink772/IRC2-token-standard
        2. https://github.com/icon-project/IIPs/blob/master/IIPS/iip-2.md
    """
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def symbol(self) -> str:
        pass

    @abstractmethod
    def decimals(self) -> int:
        pass

    @abstractmethod
    def totalSupply(self) -> int:
        pass

    @abstractmethod
    def balanceOf(self, _owner: Address) -> int:
        pass

    @abstractmethod
    def transfer(self, _to: Address, _value: int, _data: bytes=None):
        pass


class TokenFallbackInterface(InterfaceScore):
    """
    tokenFallBack interface as described in ERC223
    Ref) https://github.com/ethereum/EIPs/issues/223
    """
    @interface
    def tokenFallback(self, _from: Address, _value: int, _data: bytes):
        pass


# class LayerXToken(IconScoreBase, TokenStandard, TokenFallbackInterface):
class LayerXToken(IconScoreBase):

    # `key` of the storage
    _BALANCES = 'balances'
    _TOTAL_SUPPLY = 'total_supply'
    _OWNER = 'owner'

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        # initialize storage
        self._total_supply = VarDB(self._TOTAL_SUPPLY, db, value_type=int)
        self._balances = DictDB(self._BALANCES, db, value_type=int)

    def on_install(self, totalSupply: int) -> None:
        """constructor called during first deployment"""
        super().on_install()
        self._total_supply.set(totalSupply)

    def on_update(self) -> None:
        """constructor called during `update` deployment"""
        super().on_update()

    @external(readonly=True)
    def hello(self) -> str:
        Logger.debug(f'Hello, world!', TAG)
        return "Hello"

    @external(readonly=True)
    def balanceOf(self) -> int:
        self._total_supply.set(100)
        return 1

    @external(readonly=True)
    def name(self) -> str:
        return TAG

    @external(readonly=True)
    def symbol(self) -> str:
        return SYMBOL

    @external(readonly=True)
    def decimals(self) -> int:
        return 10

    def fallback(self):
        pass
