"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


from app import app, IntegrityError
import os
from unittest import TestCase

from models import db, User, Follow, Message, Like

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app


# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()


class UserModelTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)

        db.session.commit()
        self.u1_id = u1.id
        self.u2_id = u2.id

        self.client = app.test_client()

    def tearDown(self):
        db.session.rollback()

    def test_user_model(self):
        u1 = User.query.get(self.u1_id)

        # User should have no messages & no followers
        self.assertEqual(len(u1.messages), 0)
        self.assertEqual(len(u1.followers), 0)

    def test_is_following(self):
        """Does is_following detect when user1 IS following user2"""

        follow = Follow(user_following_id=self.u1_id,
                        user_being_followed_id=self.u2_id)

        db.session.add(follow)
        db.session.commit()

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(u1.is_following(u2), True)

    def test_is_not_following(self):
        """Does is_following detect when user1 is NOT following user2"""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(u1.is_following(u2), False)

    def test_is_followed_by(self):
        """Does is_followed_by detect when user1 IS followed by user2"""

        follow = Follow(user_following_id=self.u1_id,
                        user_being_followed_id=self.u2_id)

        db.session.add(follow)
        db.session.commit()

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(u2.is_followed_by(u1), True)

    def test_is_not_followed_by(self):
        """Does is_followed_by detect when user1 is NOT followed by user2"""

        u1 = User.query.get(self.u1_id)
        u2 = User.query.get(self.u2_id)

        self.assertEqual(u2.is_followed_by(u1), False)

    def test_user_signup_valid(self):
        """Test User.signup class method when inputs are valid"""

        u3 = User.signup("u3", "u3@email.com", "password", None)
        db.session.add(u3)
        db.session.commit()

        # Test instance properties
        self.assertIsInstance(u3, User)
        self.assertEqual(u3.username, "u3")
        self.assertEqual(u3.email, "u3@email.com")
        self.assertNotEqual(u3.password, "password")
        # will fail when Bcrypt increments
        self.assertIn("$2b$12$", u3.password)

    def test_user_signup_invalid(self):
        """Test User.signup class method when inputs are invalid"""

        try:
            u3 = User.signup("u3", "u1@email.com", "password", None)
            db.session.add(u3)
            db.session.commit()

        except IntegrityError:
            failed_duplicate_email = True
            db.session.rollback()

        try:
            u4 = User.signup("u1", "u4@email.com", "password", None)
            db.session.add(u4)
            db.session.commit()

        except IntegrityError:
            failed_duplicate_username = True
            db.session.rollback()

        try:
            User.signup("u5")

        except TypeError:
            failed_missing_fields = True

        self.assertEqual(failed_duplicate_email, True)
        self.assertEqual(failed_duplicate_username, True)
        self.assertEqual(failed_missing_fields, True)

    def test_does_user_authenticate(self):
        """tests to see if authenticate method returns correct user instance"""

        u1 = User.query.get(self.u1_id)

        u1_after_auth = User.authenticate(
            username=u1.username, password="password")

        self.assertIsInstance(u1_after_auth, User)
        self.assertEqual(u1_after_auth.username, u1.username)
        self.assertEqual(u1_after_auth.password, u1.password)
        self.assertEqual(u1_after_auth.email, u1.email)

    def test_authenticate_when_invalid(self):
        """tests to see if authenticate method returns false for either
        wrong username or wrong password"""

        # readability?
        invalid_username = User.authenticate(
            username="safdsafds", password="password")

        invalid_password = User.authenticate(
            username="u1", password="password1")

        self.assertEqual(invalid_username, False)
        self.assertEqual(invalid_password, False)

    def test_user_messages(self):
        """Test user.messages for User relationship with Message"""

        message = Message(text="Cool!", user_id=self.u1_id)
        db.session.add(message)
        db.session.commit()

        u1 = User.query.get(self.u1_id)

        self.assertEqual(len(u1.messages), 1)

    def test_user_likes(self):
        """Test user.likes for User relationsip with Like"""

        message = Message(text="Cool!", user_id=self.u1_id)
        db.session.add(message)
        db.session.commit()

        like = Like(user_id=self.u1_id, message_id=message.id)
        db.session.add(like)
        db.session.commit()

        u1 = User.query.get(self.u1_id)

        self.assertEqual(len(u1.likes), 1)
