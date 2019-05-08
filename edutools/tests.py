from Crypto import Random
from Crypto.Cipher import AES
from base64 import b64encode
import mock
import json
import unittest
from ddt import ddt

from xblock.field_data import DictFieldData

from .edutools import EduToolsXBlock


@ddt
class EduToolsXBlockTests(unittest.TestCase):
    block_id = '12345678901234567890123456789012'

    def make_one(self, **kw):
        """
        Creates a EduToolsXBlock for testing purpose.
        """
        field_data = DictFieldData(kw)
        block = EduToolsXBlock(mock.Mock(), field_data, mock.Mock())
        block.location = mock.Mock(
            block_id=self.block_id,
            org='org',
            course='course',
            block_type='block_type'
        )
        block.scope_ids = mock.Mock(usage_id=mock.Mock(block_id=self.block_id))
        return block

    def test_default_filelds_values(self):
        block = self.make_one()
        self.assertEqual(block.display_name, 'EduTools')
        self.assertEqual(block.description, 'Please run JetBtrains IDE for answer')
        self.assertEqual(block.weight, 1)

    def test_set_fields_custom_values(self):
        block = self.make_one()

        fields = {
            'display_name': 'Test EduTools',
            'description': 'Test description',
            'weight': 8
        }

        block.submit_studio_edits(mock.Mock(method="POST",
            body=json.dumps({'values': fields, 'defaults': [block.editable_fields]})))

        self.assertEqual(block.display_name, 'Test EduTools')
        self.assertEqual(block.description, 'Test description')
        self.assertEqual(block.weight, 8)

    def encrypt_score(self, score):
        iv = Random.new().read(AES.block_size)
        aes = AES.new(self.block_id, AES.MODE_CBC, iv)

        enc_string = score
        if type(score) in (float, int):
            enc_string = '{0:16.6f}'.format(score)

        return b64encode(iv + aes.encrypt(enc_string))

    def test_set_edutools_result(self):
        score = 0.567
        result = self.encrypt_score(score)

        block = self.make_one()

        resp = block.set_edutools_result(mock.Mock(method="POST", body=json.dumps({'result': result}))).json

        self.assertTrue(resp['success'])
        self.assertEqual(block.score, score)

    def test_set_edutools_result_great_then_weight(self):
        result = self.encrypt_score(1.5677)

        block = self.make_one()

        resp = block.set_edutools_result(mock.Mock(method="POST", body=json.dumps({'result': result}))).json

        self.assertTrue(resp['success'])
        self.assertEqual(block.score, block.weight)

    def test_set_edutools_result_with_no_valid_result(self):
        result = self.encrypt_score('not float string')

        block = self.make_one()

        resp = block.set_edutools_result(mock.Mock(method="POST", body=json.dumps({'result': result}))).json

        self.assertFalse(resp['success'])
