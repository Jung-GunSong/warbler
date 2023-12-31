import os
from unittest import TestCase

from models import db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

# This is a bit of hack, but don't use Flask DebugToolbar

app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class UserBaseViewTestCase(TestCase):
    def setUp(self):
        User.query.delete()

        u1 = User.signup("u1", "u1@email.com", "password", None)
        u2 = User.signup("u2", "u2@email.com", "password", None)
        db.session.flush()

        m1 = Message(text="m1-text", user_id=u1.id)
        db.session.add_all([m1])
        db.session.commit()

        self.u1_id = u1.id
        self.u2_id = u2.id
        self.m1_id = m1.id

        self.client = app.test_client()

class UserAddViewTestCase(UserBaseViewTestCase):
    def test_add_message(self):
        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

            # Now, that session setting is saved, so we can have
            # the rest of ours test
            resp = c.post("/messages/new", data={"text": "Hello"})

            self.assertEqual(resp.status_code, 302)

            Message.query.filter_by(text="Hello").one()

    def test_homepage_when_not_logged_in(self):
        """test to see if default homepage appears when logged out"""

        with self.client as c:
            resp = c.get("/")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<div class="home-hero">', html)

    def test_user_homepage_when_logged_in(self):
        """test to see if user will get custom homepage logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

        resp = c.get("/")
        html = resp.get_data(as_text=True)

        u1 = User.query.get(self.u1_id)

        self.assertEqual(resp.status_code, 200)
        self.assertIn('<!-- User homepage -->', html)
        self.assertIn(f'<img src="{u1.image_url}"', html)


    def test_other_follower_page_logged_in(self):
        """Load someone else's follower page when logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

        resp = c.get(f"/users/{self.u2_id}/followers")
        html = resp.get_data(as_text=True)

        u2 = User.query.get(self.u2_id)

        self.assertEqual(resp.status_code, 200)
        self.assertNotIn(">Access unauthorized.</div>", html)
        self.assertIn(f'<img src="{u2.image_url}"', html)
        self.assertIn('<!-- followers page -->', html)




    def test_own_follower_page_logged_in(self):
        """Load ownfollower page when logged in"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.u1_id

        resp = c.get(f"/users/{self.u1_id}/followers")
        html = resp.get_data(as_text=True)

        self.assertEqual(resp.status_code, 200)

# TODO: Ask - does html render include line breaks?
        # self.assertIn(">Edit Profile</a>", html)
        # self.assertIn(">Delete Profile</button>", html)


    def test_follower_page_logged_out(self):
        """Load follower page when logged out"""

        with self.client as c:
            resp = c.get(f"/users/{self.u2_id}/followers",
                         follow_redirects = True)
            html = resp.get_data(as_text=True)

        self.assertIn(">Access unauthorized.</div>", html)

