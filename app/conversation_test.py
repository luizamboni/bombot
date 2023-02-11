import unittest
from conversation import Conversation

class ConversationTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_imc_section(self):
        conversation = Conversation("imc", {
            "user_id": 123,
            "first_name": "another bot"
        })


        conversation.handle_response('1.75')
        conversation.handle_response('80kg')
        # sections = conversation.get_sections()
        # for section in sections:
        #     print(section["index"])
        
        data = conversation.get_data()

        self.assertEqual(data['diagnosis'], 'oversize')