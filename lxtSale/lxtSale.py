from iconservice import *

TAG = 'LXTCrowdSale'


class TokenInterface(InterfaceScore):

    @interface
    def transfer(self, _to: Address, _value: int, _data: bytes = None):
        pass


class LXTCrowdSale(IconScoreBase):

    _ADDRESS_BENEFICIARY = 'address_beneficiary'
    _ADDRESS_TOKEN_SCORE = 'address_token_score'
    _FUNDING_GOAL = 'funding_goal'
    _AMOUNT_RAISED = 'amount_raised'
    _DEAD_LINE = 'dead_line'
    _PRICE = 'price'
    _BALANCES = 'balances'
    _JOINER_LIST = 'joiner_list'
    _FUNDING_GOAL_REACHED = 'funding_goal_reached'
    _CROWDSALE_CLOSED = 'crowd_sale_closed'

    @eventlog(indexed=3)
    def FundTransfer(self, backer: Address, amount: int, is_contribution: bool):
        pass

    @eventlog(indexed=2)
    def GoalReached(self, recipient: Address, total_amount_raised: int):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._address_beneficiary = VarDB(self._ADDRESS_BENEFICIARY, db, value_type=Address)
        self._address_token_score = VarDB(self._ADDRESS_TOKEN_SCORE, db, value_type=Address)
        self._funding_goal = VarDB(self._FUNDING_GOAL, db, value_type=int)
        self._amount_raised = VarDB(self._AMOUNT_RAISED, db, value_type=int)
        self._dead_line = VarDB(self._DEAD_LINE, db, value_type=int)
        self._price = VarDB(self._PRICE, db, value_type=int)
        self._balances = DictDB(self._BALANCES, db, value_type=int)
        self._joiner_list = ArrayDB(self._JOINER_LIST, db, value_type=Address)
        self._funding_goal_reached = VarDB(self._FUNDING_GOAL_REACHED, db, value_type=bool)
        self._crowdsale_closed = VarDB(self._CROWDSALE_CLOSED, db, value_type=bool)

    def on_install(self, _fundingGoalInICX: int, _tokenScore: Address, _durationInBlock: int, _tokenToICXRatio: int) -> None:
        super().on_install()

        if _fundingGoalInICX <= 0:
            revert(f"given `_fundincGoalInICX` invalid: {_fundingGoalInICX} <= 0")

        if not _tokenScore.is_contract:
            revert("given address is not contract address")

        if _durationInBlock <= 0:
            revert(f"given `_durationInBlock` invalid: {_durationInBlock} <= 0")

        if _tokenToICXRatio <= 0:
            revert(f"given `_tokenToICXRatio` invalid: {_tokenToICXRatio} <= 0")

        self._address_beneficiary.set(self.msg.sender)
        self._address_token_score.set(_tokenScore)
        self._funding_goal.set(_fundingGoalInICX)
        self._dead_line.set(self.block_height + _durationInBlock)
        self._price.set(_tokenToICXRatio)
        self._funding_goal_reached.set(False)
        self._crowdsale_closed.set(False)

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def name(self) -> str:
        return TAG

    @external(readonly=True)
    def getTokenAddress(self) -> bytes:
        return self._address_token_score.get().to_bytes()

