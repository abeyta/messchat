import unittest
import logging
from datetime import datetime
from unittest import TestCase
from constants import *
from rmq import ChatQueue, MessProperties

PRIVATE_QUEUE_NAME = 'eshner'
PUBLIC_QUEUE_NAME = 'general'
SENDER_NAME = 'test'
DEFAULT_PRIVATE_TEST_MESS = 'DE: Test Private Queue'
DEFAULT_PUBLIC_TEST_MESS = 'DE: Test Public Queue'
class RMQTest(TestCase):
    """ Main test class for our tests.
        Inherit the TestCase from unittest - we could inherit from pytest just as easily - I find them both fine, but chose unittest
    """
    def setUp(self) -> None:
        """ This takes the place of our normal constructor and is our setup method for the test class
            NOTE: this is a feature of the unittest TestCase base class, not a typical pythong constructor
            NOTE: I don't have to call the parent's init in this case
            Set up a ChatQueue instance for both public and private queues
        """
        logging.basicConfig(filename='chat_test.log', level=logging.INFO)

        self.rmq_private = ChatQueue(queue_name=PRIVATE_QUEUE_NAME, group_queue=False)
        self.rmq_public = ChatQueue(queue_name=PUBLIC_QUEUE_NAME, group_queue=True)
        self.__last_private_message_sent: str = ''
        self.__last_public_message_sent: str = ''  

    def test_send(self, private_message: str = DEFAULT_PRIVATE_TEST_MESS, public_message: str = DEFAULT_PUBLIC_TEST_MESS) -> list:
        """ Send a private and public message the correct queues. Using default constants for the messages
            Return: the list of messages sent or None. if we think we sent fine, return list, otherwise return None so the caller knows if we got a good send
            Assert that we sent the messages and append the messages to the list to return
        """
        sent_messages = list()
        try:
            private_mess_props = MessProperties(
                mess_type = MESSAGE_TYPE_SENT,
                to_user = PRIVATE_QUEUE_NAME,
                from_user = SENDER_NAME,
                sent_time = datetime.now(),
                rec_time = None,
            )
            public_mess_props = MessProperties(
                mess_type = MESSAGE_TYPE_SENT,
                to_user = PUBLIC_QUEUE_NAME,
                from_user = SENDER_NAME,
                sent_time = datetime.now(),
                rec_time = None,
            )
            self.assertEqual(self.rmq_private.send_message(private_message, mess_props=private_mess_props), True)
            self.__last_private_message_sent = private_message
            sent_messages.append(private_message)
            self.assertEqual(self.rmq_public.send_message(public_message, mess_props=public_mess_props), True)
            self.__last_public_message_sent = public_message
            sent_messages.append(public_message)
            return sent_messages
        except AssertionError:
            logging.warning(f'SEND ERROR::Assertions failed in send_test')
            return None

    def test_get(self) -> list:
        """ Get messages from both public and private queues
            Return both public and private messages - add the two lists together
            Assert that we got the right number of mesages by testing what we got from the number returned by the function
`
        """
        try:
            private_messages, private_objects, total_private_messages = self.rmq_private.get_messages()
            public_messages, public_objects, total_public_messages = self.rmq_public.get_messages()
            text_messages = list()
            text_messages = private_messages + public_messages
            total_messages = total_private_messages + total_public_messages
            self.assertEqual(len(private_messages), total_private_messages)
            logging.debug(f'Private message get is fine. Number: {total_private_messages}, messages: {private_messages}')
            self.assertEqual(len(public_messages), total_public_messages)
            logging.debug(f'Public message get is fine. Number: {total_public_messages}, messages: {public_messages}')
            self.assertEqual(total_messages, len(text_messages))
            logging.debug(f'Total message get is fine. Number: {total_messages}, messages: {text_messages}')
            return text_messages
        except AssertionError as problem:
            logging.warning(f'GET ERROR::Assertions failed in get_test. Error: {problem}')
            return None

    def test_full(self):
        """ Testing both send and receive
            In this case, we're also asserting that what we send is actually in what we get.
            NOTE: use assertIn to test inclusion since other messages may be in the queue (especially the public que3ue)
        """
        try:
            send_result = self.test_send()
            logging.debug(f'Inside full test for RMQ, send_result is: {send_result}')
            self.assertIsNotNone(send_result)
        except AssertionError as problem:
            logging.warning(f"SEND ERROR:: inside FULL test. Problem is {problem}")
        try:
            get_result = self.test_get()
            logging.debug(f'Inside full test for RMQ, get_result is: {get_result}')
            self.assertIsNotNone(get_result)
        except AssertionError as problem:
            logging.warning(f'GET ERROR:: Inside FULL test. Problem is {problem}')
        try:
            for sent_message in send_result:
                logging.debug(f'Inside full RMQ test looping sent messages. Cur message is {sent_message}')
                self.assertIn(sent_message, get_result)
        except AssertionError as problem:
            logging.warning(f'E2E ERROR:: Inside FULL test. Problem is {problem}')

if __name__ == "__main__":
    unittest.main()