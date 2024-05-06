import pytest
from unittest.mock import patch
from ckan.lib.mailer import mail_recipient


test_email = {
    "recipient_name": "Bob",
    "recipient_email": "bob@example.com",
    "subject": "Meeting",
    "body": "The meeting is cancelled",
    "headers": {"header1": "value1"},
}


@pytest.mark.ckan_config(
    "ckan.plugins", "example_inotifier1 example_inotifier2"
)
@pytest.mark.usefixtures("with_plugins", "non_clean_db")
class TestINotifier:

    @pytest.mark.ckan_config("ckan.notifier.always_send_email", "true")
    @pytest.mark.ckan_config("ckan.notifier.notify_all", "true")
    @patch("ckan.lib.mailer._mail_recipient")
    @patch("ckanext.example_inotifier.plugin.ExampleINotifier1Plugin.notify_recipient")
    @patch("ckanext.example_inotifier.plugin.ExampleINotifier2Plugin.notify_recipient")
    def test_inotifier_full(self, nr2, nr1, mr):
        mail_recipient(**test_email)
        mr.assert_called()
        assert mr.call_args_list[0][0] == test_email["recipient_name"]

        nr1.assert_called()
        assert nr1.call_args_list[0][0] == test_email["recipient_name"]
        nr2.assert_called()
        assert nr2.call_args_list[0][0] == test_email["recipient_name"]

    @pytest.mark.ckan_config("ckan.notifier.always_send_email", "false")
    @pytest.mark.ckan_config("ckan.notifier.notify_all", "true")
    @patch("ckan.lib.mailer._mail_recipient")
    @patch("ckanext.example_inotifier.plugin.ExampleINotifier1Plugin.notify_recipient")
    @patch("ckanext.example_inotifier.plugin.ExampleINotifier2Plugin.notify_recipient")
    def test_mail_inotifier_no_mail(self, nr2, nr1, mr):
        mail_recipient(**test_email)
        # We do not send email because we send custom notifications
        mr.assert_not_called()
        nr1.assert_called()
        assert nr1.call_args_list[0][0] == test_email["recipient_name"]
        nr2.assert_called()
        assert nr2.call_args_list[0][0] == test_email["recipient_name"]

    @pytest.mark.ckan_config("ckan.notifier.always_send_email", "false")
    @pytest.mark.ckan_config("ckan.notifier.notify_all", "false")
    @patch("ckan.lib.mailer._mail_recipient")
    @patch("ckanext.example_inotifier.plugin.ExampleINotifier1Plugin.notify_recipient")
    @patch("ckanext.example_inotifier.plugin.ExampleINotifier2Plugin.notify_recipient")
    def test_inotifier_no_mail_just_one(self, nr2, nr1, mr):
        mail_recipient(**test_email)
        # We do not send email because we send custom notifications
        mr.assert_not_called()
        nr1.assert_called()
        assert nr1.call_args_list[0][0] == test_email["recipient_name"]
        # We just send the first notification
        nr2.assert_not_called()
