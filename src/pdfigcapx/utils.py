""" Utility functions invoking system packages to process PDFs """

from re import split as re_split
from os import system
from os.path import join
from subprocess import check_output
from numpy import empty_like, dot, array
from typing import List, Tuple
from pathlib import Path
from selenium import webdriver
from html_content import HtmlPage, TextLine, CountTuple


def natural_sort(arr: List[str]) -> List[str]:
    """ Sorts list in ascending order considering numpad for numbers """
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [convert(c) for c in re_split('([0-9]+)', key)]
    return sorted(arr, key=alphanum_key)


def pdf2images(file_path: str, output_path: str, dpi=500) -> None:
    """ convert PDF to images and save them on output location """
    gs_cmd = f"gs -q -sDEVICE=png16m \
        -o {join(output_path, 'file-%02d.png')} -r{dpi} {file_path}"

    # TODO: how to capture an error from the ghostscript command?
    system(gs_cmd)


def pdf2html(file_path: str, output_base_path: str) -> str:
    """ Converts PDF pages to HTML. Stores output content on a new folder
        with name xpdf_{file_path name} at output_base_path.

        Parameters
        ----------
        file_path : str
            Full path to the PDF document
        output_base_path: str
            Where to create the output folder with the HTML artifacts

        Returns
        -------
        str
            Location of the newly created folder with the artifacts

        Raises
        ------
        CalledProcessError
            If the xpdf binary pdftohtml fails to execute:
            - Error code 1 for errors opening a PDF
            - Error code 2 for using an existing folder as output folder
            - Error code 3 for PDF permissions
            - Error code 99 for anything else (e.g. missing fonts)

    """
    pdftohtml = "pdftohtml"

    document_path = Path(file_path)
    output_name = f"xpdf_{document_path.stem}"
    output_folder = Path(output_base_path) / output_name

    check_output([
        pdftohtml,
        str(document_path.resolve()),
        str(output_folder.resolve())
    ])
    return str(output_folder.resolve())


def extract_page_text_content(browser: webdriver.Chrome,
                              html_page_path: str) -> HtmlPage:
    """ Obtains page layout information and returns DIVs with text """
    html_file = f"file://{html_page_path}"
    browser.get(html_file)

    page_layout = browser.find_element_by_xpath("/html/body/img")
    text_elements = browser.find_elements_by_xpath("/html/body/div")

    text_lines = []
    for elem in text_elements:
        if len(elem.text) > 0:
            text_lines.append(
                TextLine(x0=elem.location['x'],
                         y0=elem.location['y'],
                         x1=elem.location['x'] + elem.size['width'],
                         y1=elem.location['y'] + elem.size['height'],
                         text=elem.text))
    page = HtmlPage(width=page_layout.size['width'],
                    height=page_layout.size['height'],
                    text_lines=text_lines)
    return page


def sort_by_most_common_value_desc(arr: List[int]) -> List[CountTuple]:
    """ Count ocurrences of element in arr and return sorted tuples in desc 
    order """
    counts_per_value = [
        CountTuple(value=val, count=arr.count(val)) for val in set(arr)
    ]
    # counts_per_value = [(val, arr.count(val)) for val in set(arr)]
    # return sorted(counts_per_value, key=lambda x: x.count, reverse=True)
    return sorted(counts_per_value,
                  key=lambda x: (x.count, x.value),
                  reverse=True)


def intersect_two_segments(
    point_a0: List[int],
    point_a1: List[int],
    point_q0: List[int],
    point_q1: List[int],
) -> List[int]:
    """ Find intersection between two segments 
        https://stackoverflow.com/questions/3252194/numpy-and-line-intersections
    """
    def perp(a):
        b = empty_like(a)
        b[0] = -a[1]
        b[1] = a[0]
        return b

    def seg_intersect(a1, a2, b1, b2):
        da = a2 - a1
        db = b2 - b1
        dp = a1 - b1
        dap = perp(da)
        denom = dot(dap, db)
        num = dot(dap, dp)
        return (num / denom.astype(float)) * db + b1

    intersect = seg_intersect(array(point_a0), array(point_a1),
                              array(point_q0), array(point_q1))
    intersect.astype(int)
    return [intersect[0], intersect[1]]
