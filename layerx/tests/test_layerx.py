import os

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import DeployTransactionBuilder, CallTransactionBuilder
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.signed_transaction import SignedTransaction
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


class TestLayerXToken(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '..'))

    def setUp(self):
        super().setUp()

        self.icon_service = None
        # if you want to send request to network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3
        # self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

        # install SCORE
        params = {'initialSupply': 1000, 'decimals': 10}
        self._score_address = self._deploy_score(params=params)['scoreAddress']

    def _deploy_score(self, to: str = SCORE_INSTALL_ADDRESS, params: dict = None) -> dict:
        # Generates an instance of transaction for deploying SCORE.
        transaction = DeployTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(to) \
            .step_limit(100_000_000_000) \
            .nid(3) \
            .nonce(100).params(params) \
            .content_type("application/zip") \
            .content(gen_deploy_data_content(self.SCORE_PROJECT)) \
            .build()

        # Returns the signed transaction object having a signature
        signed_transaction = SignedTransaction(transaction, self._test1)

        # process the transaction in local
        tx_result = self.process_transaction(signed_transaction, self.icon_service)

        self.assertTrue('status' in tx_result)
        self.assertEqual(1, tx_result['status'])
        self.assertTrue('scoreAddress' in tx_result)

        return tx_result

    def test_score_update(self):
        tx_result = self._deploy_score(self._score_address)

        self.assertEqual(self._score_address, tx_result['scoreAddress'])

    def test_call_name(self):
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("name") \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)

        self.assertEqual("LayerXToken", response)

    def test_call_symbol(self):
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("symbol") \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)

        self.assertEqual("LXT", response)

    def test_call_balanceOf(self):
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("balanceOf") \
            .params({"_owner": self._test1.get_address()}) \
            .build()

        # Sends the call request
        response = self.process_call(call, self.icon_service)

        self.assertEqual(hex(1000 * 10 ** 10), response)

    def test_call_transfer_success(self):
        value = 100
        recipient = f"hx{'0'*40}"

        # publish transfer calling transactions
        transaction = CallTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(self._score_address).method({}) \
            .step_limit(2000000) \
            .method("transfer") \
            .params({"_to": recipient, "_value": value}) \
            .build()

        signed_transaction = SignedTransaction(transaction, self._test1)
        tx_result = self.process_transaction(signed_transaction)

        self.assertEqual(tx_result['status'], 1)
        self.assertNotEqual(len(tx_result['eventLogs']), 0)
        print(f"eventLogs: {tx_result['eventLogs']}")

        # check the balances of recipient
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("balanceOf") \
            .params({"_owner": recipient}) \
            .build()

        response = self.process_call(call, self.icon_service)
        self.assertEqual(hex(value), response)

        # check the balances of owner
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("balanceOf") \
            .params({"_owner": self._test1.get_address()}) \
            .build()

        response = self.process_call(call, self.icon_service)
        self.assertEqual(hex(1000 * 10 ** 10 - value), response)

    def test_call_transfer_fail(self):
        value = 1000 * 10 ** 10 + 1
        recipient = f"hx{'0'*40}"

        # publish transfer calling transactions
        transaction = CallTransactionBuilder() \
            .from_(self._test1.get_address()) \
            .to(self._score_address).method({}) \
            .step_limit(2000000) \
            .method("transfer") \
            .params({"_to": recipient, "_value": value}) \
            .build()

        signed_transaction = SignedTransaction(transaction, self._test1)
        tx_result = self.process_transaction(signed_transaction)

        self.assertNotEqual(tx_result['status'], 1)
        self.assertEqual(tx_result['failure']['message'], "balance is insufficient")

        # check the balances of recipient
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("balanceOf") \
            .params({"_owner": recipient}) \
            .build()

        response = self.process_call(call, self.icon_service)
        self.assertEqual(hex(0), response)

        # check the balances of owner
        call = CallBuilder().from_(self._test1.get_address()) \
            .to(self._score_address) \
            .method("balanceOf") \
            .params({"_owner": self._test1.get_address()}) \
            .build()

        response = self.process_call(call, self.icon_service)
        self.assertEqual(hex(1000 * 10 ** 10), response)
