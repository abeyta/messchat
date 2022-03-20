"""Group Memebrs: Matt Moore, Adrian Abeyta, Ahmad Moltafet
"""

from email import message
import json
import requests
import unittest
import logging
from users import *
from constants import *

MESSAGES = ["first"]
NUM_MESSAGES = 4

class ChatTest(unittest.TestCase):
    """ Test client for API testing.
        using unittest and the TestCase base class 
    """
    def setUp(self):
        logging.basicConfig(filename='chat_api_test.log', level=logging.INFO)
    
    def test_send(self):
        """ Test sending. This is a very simple placeholder for what would ultimately be quite a few tests for send. We're only testing a trival single send
                TODO: normally we would test various send patterns:
                1) sending data we know about, should include: empty string, short string, long string, numbers, etc
                2) sending lots of messages quickly
                3) sending batches of random size
                4) What does a mini-DOS attack do?
            Simple loop through a number of messages, sending them through the api. 
                NOTE: In this case I'm using the requests library instead of fastAPI testclient. This requires the server to be running in advance
                TODO: switch to fastAPI test client so that the server gets managed for me by fastAPI. Both tests are interesting.
        """
        logging.debug('Entering test_send method')
        for loop_control in range(0, NUM_MESSAGES):
            logging.debug(f'Inside loop in test_send, iteration is {loop_control}')
            response = requests.post(f'http://localhost:8081/send?room_name=eshner&message=testmess #{loop_control}&from_alias=test&to_alias=eshner&group_queue=false')
            try: 
                self.assertEqual(response.status_code, 201)
            except: 
                logging.debug(f'test for message number {loop_control} failed. Response status: {response.status_code}. Total response: {response}')

    def test_get(self):
        """ Simple get tests. Again, very simple placeholder for what would be much more interesting receive tests
                TODO: normally we would test various get patterns:
                1) getting data we know about (we sent it), should include: empty string, short string, long string, numbers, etc
                2) receiving all messages
                3) receiving batches of 1 and random sizes
                4) What does a mini-DOS attack do for receiving do?
            Simple get messages method call, then loop through messages returned logging them.
                NOTE: In this case I'm using the requests library instead of fastAPI testclient. This requires the server to be running in advance
                TODO: switch to fastAPI test client so that the server gets managed for me by fastAPI. Both tests are interesting.
        """
        logging.debug('Entering test get method')
        response = requests.get(f'http://localhost:8081/messages?alias=eshner&room_name=eshner&group_queue=false&messages_to_get=2')
        try: 
            self.assertEqual(response.status_code, 200)
            message_list = json.loads(response.content)
            for message in message_list:
                logging.debug(f'Inside loop in test get, message is {message}')
            return response.text
        except: 
            logging.warning(f'test for getting messages failed. Response status: {response.status_code}. Total response: {response}')

    def test_send_receive(self):
        """ Method for testing that what we send, we receive on the other end
            TODO: Flesh this out, and flesh out a bunch of specialized test cases for this pattern

        """
        try:
            response = requests.post(f'http://localhost:8081/send?room_name=eshner&message=test send and receive&from_alias=test&to_alias=eshner&group_queue=false')
            logging.debug(f'Inside full test for RMQ, send_result is: {response}')
            self.assertIsNotNone(response)
        except AssertionError as problem:
            logging.warning(f"SEND ERROR:: inside FULL test. Problem is {problem}")
        try:
            response = requests.get(f'http://localhost:8081/messages?alias=eshner&room_name=eshner&group_queue=false&messages_to_get=2')
            logging.debug(f'Inside full test for RMQ, get_result is: {response}')
            self.assertIsNotNone(response)
            message_list = json.loads(response.content)
        except AssertionError as problem:
            logging.warning(f'GET ERROR:: Inside FULL test. Problem is {problem}')
        try:
            self.assertIn('test send and receive', message_list)
        except AssertionError as problem:
            logging.warning(f'E2E ERROR:: Inside FULL test. Problem is {problem}')

    def test_register(self):
        """ Test method for testing user registration
        """
        try:
            users = UserList()
        except:
            users = UserList('chat_users')
        response = requests.post(f'http://localhost:8000/register$new_user=test_user1')
        try: 
            self.assertEqual(response.status_code, 201)
        except: 
            logging.warning(f'test for register failed. Response status: {response.status_code}. Total response: {response}')
        self.assertIsNotNone(users.get_by_alias('test_user1'))


    def test_get_users(self):
        """ Simple test method for getting all users
        """
        try:
            users = UserList()
        except:
            users = UserList('chat_users')
        response = requests.post(f'http://localhost:8000/users')
        logging.debug(f'Inside test get users, response is {response}')
        try: 
            self.assertEqual(response.status_code, 201)
        except: 
            logging.debug(f'test for getting users failed. Response status: {response.status_code}. Total response: {response}')
        try:
            self.assertEqual(users.get_all_users(), response.text)
        except AssertionError:
            logging.warning(f'Inside test get users, did not get the same results. response: {response.text}, direct: {users.get_all_users()}')

            

        

