"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follow

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

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
        self.assertIn("$2b$12$", u3.password) # will fail when Bcrypt increments

    def test_user_signup_invalid(self):
        """Test User.signup class method when inputs are invalid"""