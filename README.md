[![doc](https://img.shields.io/badge/-Documentation-blue)](https://advestis.github.io/pdffactory)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

#### Status
[![pytests](https://github.com/Advestis/pdffactory/actions/workflows/pull-request.yml/badge.svg)](https://github.com/Advestis/pdffactory/actions/workflows/pull-request.yml)
[![push-pypi](https://github.com/Advestis/pdffactory/actions/workflows/push-pypi.yml/badge.svg)](https://github.com/Advestis/pdffactory/actions/workflows/push-pypi.yml)
[![push-doc](https://github.com/Advestis/pdffactory/actions/workflows/push-doc.yml/badge.svg)](https://github.com/Advestis/pdffactory/actions/workflows/push-doc.yml)

![maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg)
![issues](https://img.shields.io/github/issues/Advestis/pdffactory.svg)
![pr](https://img.shields.io/github/issues-pr/Advestis/pdffactory.svg)


#### Compatibilities
![ubuntu](https://img.shields.io/badge/Ubuntu-supported--tested-success)
![unix](https://img.shields.io/badge/Other%20Unix-supported--untested-yellow)

![python](https://img.shields.io/pypi/pyversions/pdffactory)


##### Contact
[![linkedin](https://img.shields.io/badge/LinkedIn-Advestis-blue)](https://www.linkedin.com/company/advestis/)
[![website](https://img.shields.io/badge/website-Advestis.com-blue)](https://www.advestis.com/)
[![mail](https://img.shields.io/badge/mail-maintainers-blue)](mailto:pythondev@advestis.com)

# PdfFactory

A class to update and/or create a pdf object, and add pages to it. For now only matplotlib.figure and 
tablewriter.TableWriter objects can be added.

Can be opened at the beginning of a long code to add pages from different functions. Will create a file in the 
tmp directory where pages are added, and will modify the true file when the update() method is called. update() is 
called each time and add_*() method is called. This can be prevented by passing the argument update=False to 
those methods. In that case, the user will have to call the update() method later. This can save computation time 
if a lot of pages are added during the execution of the code. 

The output file is recreated by default when update() is called for the first time. This can be switched off by 
calling will_recreate(False) before adding anything to the Pdf object. In that case, pages are appended to the 
already existing file. 


The tmp file is deleted after update() finishes, and is recreated later if need be. The tmp file might not be 
deleted if the program stops abruptly.

## Installation

`pip install pdffactory`

## Usage

```python
# noinspection PyShadowingNames
import matplotlib.pyplot as plt
import pandas as pd
from tablewriter import TableWriter
from pdffactory import PdfFactory

# Also accepts remote TransparentPath objects
pdf = PdfFactory("test.pdf")
pdf.will_recreate(False)
plt.plot([1, 2, 3], [1, 4, 9])
df = pd.DataFrame([[1, 2, 3],[4, 5, 6]], index = ["b", "a"])
tb = TableWriter(data=df)
pdf.add_figure(plt.gcf())
pdf.add_table(tb)
```
