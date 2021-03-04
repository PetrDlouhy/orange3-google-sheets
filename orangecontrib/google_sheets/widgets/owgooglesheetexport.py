import os.path
import pickle

from AnyQt.QtWidgets import QGridLayout
from Orange.data.table import Table
from Orange.widgets import gui, widget
from Orange.widgets.widget import Input
from Orange.widgets.settings import Setting
from Orange.widgets.utils.widgetpreview import WidgetPreview
from Orange.widgets.utils.state_summary import format_summary_details

from Orange.widgets.google_sheets import GSheetWriter

_userhome = os.path.expanduser(f"~{os.sep}")


class OWGoogleSheetExport(widget.OWWidget):
    name = "Google sheet export"
    description = "Exports data to Google sheets"
    icon = "icons/Save.svg"
    category = "Data"
    keywords = ["export"]

    settings_version = 1

    class Inputs:
        data = Input("Data", Table)

    class Error(widget.OWWidget.Error):
        unsupported_sparse = widget.Msg("Use Pickle format for sparse data.")

    sheet_url = Setting('')
    auto_save = Setting(True)
    delete_sheet_content = Setting(False)
    creds_token = Setting('')

    def __init__(self):
        super().__init__()

        self.info.set_input_summary(self.info.NoInput)

        self.grid = grid = QGridLayout()
        gui.widgetBox(self.controlArea, orientation=grid)
        grid.addWidget(
            gui.lineEdit(
                None, self, "sheet_url",
                "Google sheet url",
                tooltip="Fill in google sheet URL\n"
                "Should have allowed write with link",
                callback=self.update_messages),
            0, 0, 1, 100)
        grid.addWidget(
            gui.checkBox(
                None, self, "delete_sheet_content",
                "Delete whole sheet contenteet",
                tooltip="Delete sheet content\n",
                callback=self.update_messages),
            1, 0, 1, 2)
        grid.addWidget(
            gui.checkBox(
                None, self, "auto_save", "Autosave when receiving new data",
                callback=self.update_messages),
            2, 0, 1, 2)
        self.update_messages()

    def on_new_input(self):
        """
        This method must be called from input signal handler.

        - It clears errors, warnings and information and calls
          `self.update_messages` to set the as needed.
        - It also calls `update_status` the can be overriden in derived
          methods to set the status (e.g. the number of input rows)
        - Calls `self.save_sheet` if `self.auto_save` is enabled and
          `self.filename` is provided.
        """
        self.Error.clear()
        self.Warning.clear()
        self.Information.clear()
        self.update_messages()
        self.update_status()
        if self.auto_save and self.sheet_url:
            self.save_sheet()

    @Inputs.data
    def dataset(self, data):
        self.data = data
        self.on_new_input()

    def save_sheet(self):
        """
        If file name is provided, try saving, else call save_file_as
        """
        if self.data:
            self.do_save()

    def do_save(self):
        if self.data.is_sparse() and not self.writer.SUPPORT_SPARSE_DATA:
            return
        try:
            creds_token = pickle.loads(self.creds_token)
        except TypeError:
            creds_token = None
        creds_token = GSheetWriter.write_sheet(
            self.data, self.sheet_url, self.delete_sheet_content,
            creds_token,
        )
        self.creds_token = pickle.dumps(creds_token)

    def update_messages(self):
        pass
        # self.Error.no_file_name(shown=not self.filename and self.auto_save)
        # self.Information.empty_input(
        # shown=self.filename and self.data is None)
        # self.Error.unsupported_sparse(
        #     shown=self.data is not None and self.data.is_sparse()
        #     and self.filename and not self.writer.SUPPORT_SPARSE_DATA)

    def update_status(self):
        summary = len(self.data) if self.data else self.info.NoInput
        details = format_summary_details(self.data) if self.data else ""
        self.info.set_input_summary(summary, details)

    def send_report(self):
        self.report_data_brief(self.data)
        writer = self.writer
        noyes = ["No", "Yes"]
        self.report_items((
            ("File name", self.filename or "not set"),
            ("Format", writer.DESCRIPTION),
            ("Type annotations",
             writer.OPTIONAL_TYPE_ANNOTATIONS
             and noyes[self.add_type_annotations])
        ))


if __name__ == "__main__":  # pragma: no cover
    WidgetPreview(OWGoogleSheetExport).run(Table("iris"))
