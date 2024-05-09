from typing import Any, Dict, Iterable

from formtools.wizard.storage.session import SessionStorage as WizardSessionStorage


class SessionStorage(WizardSessionStorage):
    def get_step_data(self, step: str) -> Dict[str, Any] | None:
        if step == "about_the_end_user":
            if end_user_uuid := self.request.resolver_match.kwargs.get("end_user_uuid", None):
                if end_user_dict := self.request.session.get("end_users", {}).get(end_user_uuid, None):
                    return end_user_dict["dirty_data"]
            else:
                return None

        if step == "end_user_added":
            # we don't want to remember people's choices for this step, if they want to add a new end user will change
            # each time they come back to this step
            return None
        return super().get_step_data(step)

    def reset(self) -> None:
        # Store unused temporary file names in order to delete them
        # at the end of the response cycle through a callback attached in
        # `update_response`.
        wizard_files = self.data[self.step_files_key]
        for step_files in wizard_files.values():
            for step_file in step_files.values():
                self._tmp_files.append(step_file["tmp_name"])
        self.request.session.pop("end_users", None)
        self.request.session.pop("made_available_journey", None)
        self.request.session.pop("file_uploads", None)
        self.request.session.modified = True
        self.init_data()

    def delete_step_data(self, *steps: Iterable[str]) -> None:
        for step in steps:
            self.data[self.step_data_key].pop(step, None)
