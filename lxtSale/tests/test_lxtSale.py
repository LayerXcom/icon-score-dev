import os

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import DeployTransactionBuilder
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.signed_transaction import SignedTransaction
from tbears.libs.icon_integrate_test import IconIntegrateTestBase, SCORE_INSTALL_ADDRESS

DIR_PATH = os.path.abspath(os.path.dirname(__file__))


# (self, _fundingGoalInICX: int, _tokenScore: Address, _durationInBlock: int, _tokenToICXRatio: int
class TestLXTCrowdSale(IconIntegrateTestBase):
    TEST_HTTP_ENDPOINT_URI_V3 = "http://127.0.0.1:9000/api/v3"
    TOKEN_SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '../../layerx'))
    TOKEN_SCORE_PARAM = {
        "initialSupply": 10000,
        "decimals": 1000
    }

    CROWDSALE_SCORE_PROJECT = os.path.abspath(os.path.join(DIR_PATH, '..'))
    CROWDSALE_PARAM = {
        "_fundingGoalInICX": 1000000,
        "_tokenScore": None,
        "_durationInBlock": 100,
        "_tokenToICXRatio": 10
    }

    def setUp(self):
        super().setUp()

        self.icon_service = None
        # if you want to send request to network, uncomment next line and set self.TEST_HTTP_ENDPOINT_URI_V3
        # self.icon_service = IconService(HTTPProvider(self.TEST_HTTP_ENDPOINT_URI_V3))

        # install SCORE
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
