import tempfile
from pathlib import Path
from typing import BinaryIO, Union
import warnings
import PyPDF2
from matplotlib import pyplot as plt
from matplotlib.backends import backend_pdf as pltpdf

from tablewriter import TableWriter


# noinspection PyUnresolvedReferences
def unlink_if_exists(path: Union[Path, "TransparentPath"]) -> None:
    """Removes the file if it exists.

    Else, does nothing.
    """
    if path.is_file():
        path.unlink()


class PdfFactory(object):
    """A class to update and/or create a pdf object, and add pages to it. For now only matplotlib.figure and
    tablewriter.TableWriter objects can be added.

    Can be opened at the beginning of a long code to add pages from different functions. Will create a file in the
    tmp directory were pages are added, and will modify the true file when the update() method is called. update() is
    called each time and add_*() method is called. This can be prevented by passing the argument update=False to
    those method. In that case, the user will have to call the update() method later. This can save computation time
    if a lot of pages are added during the execution of the code.

    The output file is recreated by default when update() is called for the first time. This can be switched off by
    calling will_recreate(False) before adding anything to the Pdf object. In that case, pages are appended to the
    already existing file.


    The tmp file is deleted after update() finishes, and is recreated later if need be. The tmp file might not be
    deleted if the program stops abruptly.

    Examples
    --------

    >>> # noinspection PyShadowingNames
    >>> import matplotlib.pyplot as plt  # doctest: +SKIP
    >>> import pandas as pd  # doctest: +SKIP
    >>> from tablewriter import TableWriter  # doctest: +SKIP
    >>> from pdffactory import PdfFactory  # doctest: +SKIP

    >>> # Also accepts remote TransparentPath objects
    >>> pdf = PdfFactory("test.pdf")  # doctest: +SKIP
    >>> pdf.will_recreate(False)  # doctest: +SKIP
    >>> plt.plot([1, 2, 3], [1, 4, 9])  # doctest: +SKIP
    >>> df = pd.DataFrame([[1, 2, 3],[4, 5, 6]], index = ["b", "a"])  # doctest: +SKIP
    >>> tb = TableWriter(data=df)  # doctest: +SKIP
    >>> pdf.add_figure(plt.gcf())  # doctest: +SKIP
    >>> pdf.add_table(tb)  # doctest: +SKIP
    """

    SILENCED = True
    logger = None

    @classmethod
    def set_silenced(cls, silenced: bool) -> None:
        """To not print anything (except errors)"""
        cls.SILENCED = silenced

    # noinspection PyUnresolvedReferences
    def __init__(
        self, path: Union[str, Path, "TransparentPath"],
    ):
        """

        Parameters
        ----------
        path: Union[str, Path, "TransparentPath"] : Were the pdf file will be (or is) stored.
            Initialisation does not touch the file located at path.
        """

        if type(path) == str:
            path = Path(path)
        self.path = path
        self.recreated = False
        self.path_tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

        PdfFactory.log(f"created tmp file {self.path_tmp.name}", "debug")
        PdfFactory.log(f"test existence of tmp file : {Path(self.path_tmp.name).is_file()}", "debug")

    def __del__(self):
        PdfFactory.log(f"deleting tmp file {self.path_tmp.name}", "debug")
        unlink_if_exists(Path(self.path_tmp.name, fs="local"))

    def will_recreate(self, b: bool = True) -> None:
        """If True (default behavior), previous file is overwriten. Else,
        appends the new pages to it.

        Parameters
        ----------
        b: bool
            Default True
        """
        self.recreated = not b

    def add_figure(self, fig: plt.figure, update: bool = True, recreate: bool = False) -> None:
        """To add a page containing a matplotlib.pyplot figure.

        Parameters
        ----------
        fig: plt.figure : the figure object to add
        update: bool
            If true, updates the file located at self.path. If False,
            update must be done later by calling update() or by
            calling any add_something() method with update=True.
            Default True.
        recreate: bool :
            If True, any file found at self.path will be overwritten.
            Only valid if update is True.
            Default False.
        """

        if not isinstance(fig, plt.Figure):
            raise ValueError(f"Only accepts matplotlib.figure.Figure object, not {type(fig)}")

        PdfFactory.log("Adding a figure", "debug")
        pdf = pltpdf.PdfPages(self.path_tmp.name)
        pdf.savefig(fig, bbox_inches="tight")
        pdf.close()
        if update:
            # If recreate is specified, recreates the file.
            # If it is the first time that add_something() was called, also
            # recreated the file
            self.update(recreate or not self.recreated)
            self.recreated = True

    def add_table(self, table: TableWriter, update: bool = True, recreate: bool = False) -> None:
        """To add a page containing a matplotlib.pyplot figure.

        Parameters
        ----------
        table: TableWriter : the table object to add
        update: bool
            If true, updates the file located at self.path. If False,
            update must be done later by calling update() or by
            calling any add_something() method with update=True.
            Default True.
        recreate: bool :
            If True, any file found at self.path will be overwritten.
            Only valid if update is True.
            Default False.
        """

        if not isinstance(table, TableWriter):
            raise ValueError(f"Only accepts TableWriter object, not {type(table)}")

        PdfFactory.log("Adding a table", "debug")
        table.path = self.path_tmp.name
        table.compile(silenced=PdfFactory.SILENCED, clean_tex=True)
        if update:
            # If recreate is specified, recreates the file.
            # If it is the first time that add_something() was called, also
            # recreated the file
            self.update(recreate or not self.recreated)
            self.recreated = True

    # noinspection PyBroadException,PyUnresolvedReferences
    def get_pdf_pages(
        self, path: Union[Path, "TransparentPath", str], out: PyPDF2.PdfFileWriter
    ) -> Union[BinaryIO, None]:
        """To get existing pages in a given pdf file.

        Will raise an error if the file exists by failed to read.

        Parameters
        ----------
        path: Union[Path, TransparentPath, str] : The path to read pages from
        out: PyPDF2.PdfFileWriter :
         The object in which to store those pages

        Returns
        -------
        Union[BinaryIO, None]
            The opened file at path if successfully read, None if no
            file were found.
        """

        if type(path) == str:
            path = Path(path)
        PdfFactory.log(f"  getting pdf pages from {path}", "debug")
        if path.is_file():
            PdfFactory.log(f"    found the file {path}", "debug")
            try:
                f = open(path, "rb")
                pdf = PyPDF2.PdfFileReader(f)
                for ipage in range(pdf.getNumPages()):
                    out.addPage(pdf.getPage(ipage))
                return f
            except Exception as e:
                Path(self.path_tmp.name).unlink()
                raise e

        PdfFactory.log(f"    did not find the file {path}", "debug")
        return None

    def update(self, recreate: bool = False) -> None:
        """Updates the file located at self.path. Will overwrite any existing
        file at self.path if recreate is True.

        Parameters
        ----------
        recreate: bool : Overwrite any existing file at self.path if True.
            Else, update it with the new pages.
            Default False.
        """

        output = PyPDF2.PdfFileWriter()

        f_old = None
        if not recreate:

            PdfFactory.log(f"fetching old file {self.path}", "debug")
            f_old = self.get_pdf_pages(self.path, output)

        PdfFactory.log(f"fetching tmp file {self.path_tmp.name}", "debug")
        f_new = self.get_pdf_pages(Path(self.path_tmp.name, fs="local"), output)

        if "append" in dir(self.path):
            with open(self.path.append("_"), "wb") as outputStream:
                output.write(outputStream)
        else:
            with open(str(self.path) + "_", "wb") as outputStream:
                output.write(outputStream)

        if f_old is not None:
            f_old.close()
        if f_new is not None:
            f_new.close()

        self.path_tmp.close()

        PdfFactory.log(f"deleting tmp file {self.path_tmp.name}", "debug")
        unlink_if_exists(Path(self.path_tmp.name, fs="local"))
        if "append" in dir(self.path):
            self.path.append("_").mv(self.path)
        else:
            Path(str(self.path) + "_").rename(self.path)

    @classmethod
    def log(cls, message, type_):
        if cls.logger is None:
            if type_ == "error" or type_ == "critical":
                if isinstance(message, BaseException):
                    raise message
                else:
                    raise ValueError(message)
            elif type_ == "warning":
                warnings.warn(message)
            elif type_ != "debug":
                print(message)
        else:
            getattr(cls.logger, type_)(message)
