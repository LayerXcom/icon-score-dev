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
class LayerXToken(IconScoreBase, TokenStandard):

    # `key` of the storage
    _BALANCES = 'balances'
    _TOTAL_SUPPLY = 'total_supply'
    _DECIMALS = 'decimals'
    _OWNER = 'owner'

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        # initialize storage
        self._total_supply = VarDB(self._TOTAL_SUPPLY, db, value_type=int)
        self._balances = DictDB(self._BALANCES, db, value_type=int)
        self._decimals = VarDB(self._DECIMALS, db, value_type=int)

    def on_install(self, initialSupply: int, decimals: int) -> None:
        """constructor called during first deployment"""
        super().on_install()

        if initialSupply <= 0:
            revert(f"given `initialSupply` invalid: {initialSupply} <= 0")

        if decimals <= 0:
            revert(f"given `decimals` invalid: {decimals} <= 0")

        total_supply = initialSupply * 10 ** decimals
        self._total_supply.set(initialSupply)
        self._decimals.set(decimals)
        self._balances[self.msg.sender] = total_supply

    def on_update(self) -> None:
        """constructor called during `update` deployment"""
        super().on_update()

    @external(readonly=True)
    def name(self) -> str:
        return TAG

    @external(readonly=True)
    def symbol(self) -> str:
        return SYMBOL

    @external(readonly=True)
    def decimals(self) -> int:
        return self._decimals.get()

    def fallback(self):
        pass

    @external(readonly=True)
    def totalSupply(self) -> int:
        return self._total_supply.get()

    @external(readonly=True)
    def balanceOf(self, _owner: Address) -> int:
        return self._balances[_owner]

    @external
    def transfer(self, _to: Address, _value: int, _data: bytes = None):
        if _data is None:
            _data = b'None'

        self._transfer(self.msg.sender, _to, _value, _data)

    def _transfer(self, _from: Address, _to: Address, _value: int, _data: bytes):

        if self._balances[_from] < _value:
            revert("balance is insufficient")

        self._balances[_from] -= _value
        self._balances[_to] += _value

        # call tokenFallback function if the target address is contract address
        if _to.is_contract:
            _target = self.create_interface_score(_to, TokenFallbackInterface)
            _target.tokenFallback(_from, _value, _data)

        # event logging
        self.Transfer(_from, _to, _value, _data)

    @eventlog(indexed=3)
    def Transfer(self, _from: Address, _to: Address, _value: int, _data: bytes):
        pass
