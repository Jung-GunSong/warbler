"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py
import os

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app, IntegrityError, DataError
from unittest import TestCase

from models import db, User, Message, Follow

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database


# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class MessageModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id

        m1 = Message(user_id=self.u1_id, text="Message 1 by user 1!")
        m2 = Message(user_id=self.u2_id, text="Message 2 by user 2!")

        db.session.add(m1)
        db.session.add(m2)
        db.session.commit()

        self.m1_id = m1.id
        self.m2_id = m2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_message_model(self):
        """Test model itself."""

        m1 = Message.query.get(self.m1_id)

        self.assertIsInstance(m1.user, User)
        self.assertIsInstance(m1, Message)

    def test_create_message_valid(self):
        """Create message with valid inputs"""

        m3 = Message(user_id=self.u1_id, text="Another message!")
        db.session.add(m3)
        db.session.commit()

        self.assertEqual(Message.query.count(), 3)
        self.assertIsInstance(m3, Message)
        self.assertEqual(m3.text, "Another message!")
        self.assertEqual(m3.user.id, self.u1_id)

    def test_create_message_invalid(self):

        """tests message creation with either no username or text"""

        try:
            message_with_no_user_id = Message(text="Another message!")
            db.session.add(message_with_no_user_id)
            db.session.commit()

        except IntegrityError:
            failure_from_no_user_id = True
            db.session.rollback()

        try:
            message_with_no_text = Message(user_id=self.u1_id)
            db.session.add(message_with_no_text)
            db.session.commit()

        except IntegrityError:
            failure_from_no_text = True
            db.session.rollback()

        self.assertEqual(failure_from_no_user_id,True)
        self.assertEqual(failure_from_no_text,True)

    def test_deleting_message(self):

        """tests message deletion"""

        m1 = Message.query.get(self.m1_id)
        db.session.delete(m1)
        db.session.commit()

        self.assertEqual(Message.query.count(), 1)
        self.assertNotIn(m1, Message.query.all())

    def test_edit_message_valid(self):

        """test if message can be edited with valid inputs"""

        m1 = Message.query.get(self.m1_id)
        m1.text = "I'm a new message now!"
        db.session.commit()

        self.assertEqual(Message.query.get(self.m1_id).text,
                         m1.text)

    def test_edit_message_invalid(self):

        """test if message can be edited with invalid inputs"""

        try:
            m1 = Message.query.get(self.m1_id)
            m1.text = """Lorem ipsum dolor sit amet, consectetuer adipiscing
                         elit. Aenean commodo ligula eget dolor. Aenean massa
                         Cum sociis natoque penatibus et mag"""

            db.session.commit()
        except DataError:
            failure_from_too_much_text = True

        self.assertEqual(failure_from_too_much_text, True)

    # def test_is_liked_already(self):
    #     """test is_liked_already instance method"""