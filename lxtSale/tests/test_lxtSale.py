import os

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import DeployTransactionBuilder, CallTransactionBuilder, TransactionBuilder
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.signed_transaction import SignedTransaction
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class TestLXTCrowdSale(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    TOKEN_SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '../../layerx'))
    TOKEN_SCORE_PARAM = {
        "initialSupply": 10000,
        "_decimals": 1000
    }

    CROWDSALE_SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '..'))
    CROWDSALE_PARAM = {
        "_fundingGoalInICX": 5,
        "_tokenScore": None,
        "_durationInBlock": 1,
        "_tokenToICXRatio": 10
    }

    def setUp(self):
        super().setUp()
        self.icon_service = None

        # deploy
        _deploy_result = self._deploy_score()
        self.crowdsale_score_address = _deploy_result['crowdsale_score_address']
        self.token_score_address = _deploy_result['token_score_address']

    def _deploy_score(self, to: str = SCORE_INSTALL_ADDRESS) -> dict:
        # publish token score contract
        transaction = DeployTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(to) \
            .step_limit(100_000_000_000) \
            .nid(3) \
            .nonce(100).params(self.TOKEN_SCORE_PARAM)  \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(self.TOKEN_SCORE_PROJECT)) \
            .build()

        signed_transaction = SignedTransaction(transaction, self._test1)
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])
        self.assertTrue('scoreAddress' in tx_result)

        # publish crowdsale score contract
        self.CROWDSALE_PARAM['_tokenScore'] = tx_result['scoreAddress']

        transaction = DeployTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(to) \
            .step_limit(100_000_000_000) \
            .nid(3) \
            .nonce(100).params(self.CROWDSALE_PARAM)  \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(self.CROWDSALE_SCORE_PROJECT)) \
            .build()

        signed_transaction = SignedTransaction(transaction, self._test1)
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])
        self.assertTrue('scoreAddress' in tx_result)
        return {
            'crowdsale_score_address': tx_result['scoreAddress'],
            'token_score_address': self.CROWDSALE_PARAM['_tokenScore']
        }

    def test_call_name(self):
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self.crowdsale_score_address) \
            .method("name") \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        self.assertEqual("LXTCrowdSale", response)

        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self.token_score_address) \
            .method("name") \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        self.assertEqual("LayerXToken", response)

    def test_get_token_address(self):
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self.crowdsale_score_address) \
            .method("getTokenAddress") \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        self.assertEqual(self.token_score_address, response)

    def test_total_joiner_count(self):
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self.crowdsale_score_address) \
            .method("totalJoinerCount") \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        self.assertEqual(hex(0), response)

    def test_amount_raised(self):
        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self.crowdsale_score_address) \
            .method("amountRaised") \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        self.assertEqual(hex(0), response)

    def test_token_fallback(self):
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self.crowdsale_score_address) \
            .method("isCrowdsaleClosed") \
            .build()

        response = self.process_call(call, self.icon_service)
        self.assertEqual(hex(True), response)

        transaction = CallTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(self.token_score_address).method({}) \
            .step_limit(2000000) \
            .method("transfer") \
            .params({"_to": self.crowdsale_score_address, "_value": 100}) \
            .build()

        signed_transaction = SignedTransaction(transaction, self._test1)
        _ = self.process_transaction(signed_transaction)

        # Generates a call instance using the CallBuilder
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self.crowdsale_score_address) \
            .method("isCrowdsaleClosed") \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)
        self.assertEqual(hex(False), response)

    def test_fallback(self):
        donation = 10

        transaction = CallTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(self.token_score_address).method({}) \
            .step_limit(2000000) \
            .method("transfer") \
            .params({"_to": self.crowdsale_score_address, "_value": 1000}) \
            .build()

        signed_transaction = SignedTransaction(transaction, self._test1)
        tx_result = self.process_transaction(signed_transaction)
        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

        transaction = TransactionBuilder()\
            .from_(self._test1.get_address())\
            .to(self.crowdsale_score_address)\
            .step_limit(2000000)\
            .value(donation)\
            .build()

        signed_transaction = SignedTransaction(transaction, self._test1)
        tx_result = self.process_transaction(signed_transaction)
        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self.crowdsale_score_address) \
            .method("isCrowdsaleClosed") \
            .build()
        response = self.process_call(call, self.icon_service)
        self.assertEqual(hex(False), response)

        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self.crowdsale_score_address) \
            .method("totalJoinerCount") \
            .build()
        response = self.process_call(call, self.icon_service)
        self.assertEqual(hex(1), response)

        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self.crowdsale_score_address) \
            .method("amountRaised") \
            .build()

        response = self.process_call(call, self.icon_service)
        self.assertEqual(hex(donation), response)

    def test_check_goal_reached(self):
        donation = 10
        transaction = CallTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(self.token_score_address).method({}) \
            .step_limit(2000000) \
            .method("transfer") \
            .params({"_to": self.crowdsale_score_address, "_value": 1000}) \
            .build()

        signed_transaction = SignedTransaction(transaction, self._test1)
        tx_result = self.process_transaction(signed_transaction)
        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

        transaction = TransactionBuilder()\
            .from_(self._test1.get_address())\
            .to(self.crowdsale_score_address)\
            .step_limit(2000000)\
            .value(donation)\
            .build()

        signed_transaction = SignedTransaction(transaction, self._test1)
        tx_result = self.process_transaction(signed_transaction)
        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

        transaction = CallTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(self.crowdsale_score_address).method({}) \
            .step_limit(2000000) \
            .method("checkGoalReached") \
            .build()

        signed_transaction = SignedTransaction(transaction, self._test1)
        tx_result = self.process_transaction(signed_transaction)
        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])

        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self.crowdsale_score_address) \
            .method("isCrowdsaleClosed") \
            .build()

        response = self.process_call(call, self.icon_service)
        self.assertEqual(hex(True), response)

        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self.crowdsale_score_address) \
            .method("isFundingGoalReached") \
            .build()

        response = self.process_call(call, self.icon_service)
        self.assertEqual(hex(True), response)
