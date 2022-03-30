import matplotlib.pyplot as plt
import pandas as pd
import pytest
from tablewriter import TableWriter
from pdffactory import PdfFactory
from pathlib import Path


@pytest.mark.parametrize(
    "cls", [Path, str]
)
def test_pdffactory(cls):
    PdfFactory.SILENCED = False

    outpath = Path("tests/data/out.pdf")
    if outpath.is_file():
        outpath.unlink()
    outpath = cls(str(outpath))

    pdf = PdfFactory(outpath)
    pdf.will_recreate(True)
    plt.plot([1, 2, 3], [1, 4, 9])
    df = pd.DataFrame([[1, 2, 3], [4, 5, 6]], index=["b", "a"])
    tb = TableWriter(data=df)
    pdf.add_figure(plt.gcf())
    pdf.add_table(tb)
    if cls == str:
        cls = Path
    assert cls(outpath).is_file()
    cls(outpath).unlink()
