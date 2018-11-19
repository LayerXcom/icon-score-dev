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
        self._crowdsale_closed.set(True)

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def name(self) -> str:
        return TAG

    @external(readonly=True)
    def getTokenAddress(self) -> str:
        return self._address_token_score.get()

    @external(readonly=True)
    def totalJoinerCount(self) -> int:
        return len(self._joiner_list)

    @external(readonly=True)
    def amountRaised(self) -> int:
        return self._amount_raised.get()

    def _after_deadline(self) -> bool:
        return self.block_height >= self._dead_line.get()

    @external(readonly=True)
    def isCrowdsaleClosed(self) -> bool:
        return self._crowdsale_closed.get()

    @external
    def tokenFallback(self, _from: Address, _value: int, _data: bytes = None):
        """
        implement `tokenFallBack` interface in order for this contract
         to receive tokens for distributing them in response to donations (as in fallback function)
        """

        if self.msg.sender != self._address_token_score.get():
            revert("Unknown token address")

        if _from != self.owner:
            revert("Invalid sender")

        if _value <= 0:
            revert(f"given `_value` invalid: {_value} <= 0")

        self._crowdsale_closed.set(False)

    @payable
    def fallback(self):
        if self._crowdsale_closed.get():
            revert("crowdsale is already closed")

        self._balances[self.msg.sender] += self.msg.value
        self._amount_raised.set(self._amount_raised.get() + self.msg.value)

        token_score = self.create_interface_score(self._address_token_score.get(), TokenInterface)
        token_score.transfer(self.msg.sender, int(self.msg.value / self._price.get()), b'')

        if self.msg.sender not in self._joiner_list:
            self._joiner_list.put(self.msg.sender)

        self.FundTransfer(self.msg.sender, self.msg.value, True)
