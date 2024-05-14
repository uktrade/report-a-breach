from unittest.mock import MagicMock, PropertyMock, patch

from django.urls import reverse
from report_a_suspected_breach import tasklist


class TestTasklist:
    def test_current_task(self, rasb_client):
        response = rasb_client.get(reverse("report_a_suspected_breach:landing"))
        assert isinstance(response.tasklist.current_task, tasklist.YourDetailsTask)

        response = rasb_client.get(
            reverse("report_a_suspected_breach:step", kwargs={"step": "are_you_reporting_a_business_on_companies_house"}),
            data={"start": "true"},
        )
        assert isinstance(response.tasklist.current_task, tasklist.AboutThePersonOrBusinessTask)

        response = rasb_client.get(
            reverse("report_a_suspected_breach:step", kwargs={"step": "when_did_you_first_suspect"}), data={"start": "true"}
        )
        assert isinstance(response.tasklist.current_task, tasklist.OverviewOfTheSuspectedBreachTask)

        response = rasb_client.get(
            reverse("report_a_suspected_breach:step", kwargs={"step": "where_were_the_goods_supplied_from"}),
            data={"start": "true"},
        )
        assert isinstance(response.tasklist.current_task, tasklist.TheSupplyChainTask)

        response = rasb_client.get(
            reverse("report_a_suspected_breach:step", kwargs={"step": "tell_us_about_the_suspected_breach"}),
            data={"start": "true"},
        )
        assert isinstance(response.tasklist.current_task, tasklist.SanctionsBreachDetailsTask)

    def test_should_show_task_list_page(self, rasb_client):
        response = rasb_client.get(reverse("report_a_suspected_breach:landing"))
        assert response.tasklist.should_show_task_list_page() is True

        response = rasb_client.get(reverse("report_a_suspected_breach:step", kwargs={"step": "email"}), data={"start": "true"})
        assert response.tasklist.should_show_task_list_page() is False

    def test_underscored_task_name(self, rasb_client):
        response = rasb_client.get(reverse("report_a_suspected_breach:landing"))
        assert response.tasklist.current_task.underscored_task_name == "your_details"

    def test_can_start(self, rasb_client):
        response = rasb_client.get(reverse("report_a_suspected_breach:landing"))
        assert response.tasklist.tasks[0].can_start
        assert all(not task.can_start for task in response.tasklist.tasks[1:])

        # testing that if the first task is complete, the second task can start
        with patch("report_a_suspected_breach.tasklist.YourDetailsTask") as mock_your_details_task:
            mock_your_details_task.complete = True

            response = rasb_client.get(
                reverse("report_a_suspected_breach:step", kwargs={"step": "are_you_reporting_a_business_on_companies_house"}),
                data={"start": "true"},
            )
            assert response.tasklist.tasks[1].can_start
            assert all(not task.can_start for task in response.tasklist.tasks[2:])

    def test_not_complete_at_start(self, rasb_client):
        response = rasb_client.get(reverse("report_a_suspected_breach:landing"))

        # asserting none of the tasks are complete at first entry
        assert all([not task.complete for task in response.tasklist.tasks])

    @patch("report_a_suspected_breach.session.SessionStorage.get_step_data")
    def test_not_complete_partial(self, mock_get_step_data, rasb_client):
        """testing that if not all the compulsory steps are complete, the overall task is not complete."""

        # mocking the first 2 steps done, 'verify' is still remaining
        def fake_step_data(step):
            if step == "start":
                return {True: True}
            else:
                return {}

        mock_get_step_data.side_effect = fake_step_data

        response = rasb_client.get(reverse("report_a_suspected_breach:landing"))
        assert not response.tasklist.tasks[0].complete

    @patch("report_a_suspected_breach.session.SessionStorage.get_step_data")
    def test_complete_optional_fields_missing(self, mock_get_step_data, rasb_client):
        """Testing that if only optional fields are missing, the task is still complete."""

        # mocking the first 3 compulsory steps done
        def fake_step_data(step):
            if step in ["start", "email", "verify"]:
                return {True: True}
            else:
                return {}

        mock_get_step_data.side_effect = fake_step_data

        response = rasb_client.get(reverse("report_a_suspected_breach:landing"))
        assert response.tasklist.tasks[0].complete

    def test_get_tasklist(self):
        mock_wizard_view = MagicMock()
        tasklist_object = tasklist.get_tasklist(mock_wizard_view)
        assert isinstance(tasklist_object, tasklist.TaskList)
        for task in tasklist_object.tasks:
            assert isinstance(task, tasklist.Task)

    @patch("report_a_suspected_breach.tasklist.Task.complete", new_callable=PropertyMock)
    def test_status_complete(self, mocked_complete):
        mock_wizard_view = MagicMock()
        mock_task_list = MagicMock()
        mocked_complete.return_value = True
        assert tasklist.Task(mock_wizard_view, mock_task_list).status == "Completed"

    @patch("report_a_suspected_breach.tasklist.Task.complete", new_callable=PropertyMock)
    @patch("report_a_suspected_breach.tasklist.Task.can_start", new_callable=PropertyMock)
    def test_status_can_start(self, mocked_can_start, mocked_complete):
        mocked_complete.return_value = False
        mocked_can_start.return_value = True

        mock_wizard_view = MagicMock()
        mock_task_list = MagicMock()
        assert tasklist.Task(mock_wizard_view, mock_task_list).status == "Not yet started"

    @patch("report_a_suspected_breach.tasklist.Task.complete", new_callable=PropertyMock)
    @patch("report_a_suspected_breach.tasklist.Task.can_start", new_callable=PropertyMock)
    def test_status_default(self, mocked_can_start, mocked_complete):
        mock_wizard_view = MagicMock()
        mock_task_list = MagicMock()
        mocked_complete.return_value = False
        mocked_can_start.return_value = False
        assert tasklist.Task(mock_wizard_view, mock_task_list).status == "Cannot start yet"

    def test_first_task_can_start(self):
        """Tests that the first task in the tasklist can always be started so long as it is not complete."""
        mock_wizard_view = MagicMock()
        mock_task_list = MagicMock()

        with patch("report_a_suspected_breach.tasklist.YourDetailsTask.complete", new_callable=PropertyMock) as mock_complete:
            mock_complete.return_value = False
            assert tasklist.YourDetailsTask(mock_wizard_view, mock_task_list).can_start

        with patch("report_a_suspected_breach.tasklist.YourDetailsTask.complete", new_callable=PropertyMock) as mock_complete:
            mock_complete.return_value = True
            assert not tasklist.YourDetailsTask(mock_wizard_view, mock_task_list).can_start
