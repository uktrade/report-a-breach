from formtools.wizard.storage.session import SessionStorage as WizardSessionStorage


class SessionStorage(WizardSessionStorage):
    def get_step_data(self, step):
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

    def delete_step_data(self, *steps):
        for step in steps:
            self.data[self.step_data_key].pop(step, None)

    def set_step_files(self, step, files):
        """Overwriting this to prepend the session key to the file name. This is to avoid conflicts when multiple users
        upload files with the same name."""
        if step not in self.data[self.step_files_key]:
            self.data[self.step_files_key][step] = {}

        for field, field_file in (files or {}).items():
            session_keyed_file_name = f"{self.request.session.session_key}/{field_file.name}"
            tmp_filename = self.file_storage.save(session_keyed_file_name, field_file)
            file_dict = {
                "tmp_name": tmp_filename,
                "name": field_file.name,
                "content_type": field_file.content_type,
                "size": field_file.size,
                "charset": field_file.charset,
            }
            self.data[self.step_files_key][step][field] = file_dict