import matplotlib.pyplot as plt
import pandas as pd
from tablewriter import TableWriter
from pdffactory import PdfFactory
from transparentpath import TransparentPath as Path


def test_pdffactory():
    PdfFactory.SILENCED = False

    outpath = Path("tests/data/out.pdf")
    if outpath.is_file():
        outpath.rm()

    pdf = PdfFactory(outpath)
    pdf.will_recreate(True)
    plt.plot([1, 2, 3], [1, 4, 9])
    df = pd.DataFrame([[1, 2, 3], [4, 5, 6]], index=["b", "a"])
    tb = TableWriter(data=df)
    pdf.add_figure(plt.gcf())
    pdf.add_table(tb)
    assert outpath.is_file()

test_pdffactory()