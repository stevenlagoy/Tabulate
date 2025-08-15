from io import TextIOWrapper
from typing import List, Dict, Any
import re
import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

class Cell:
  def __init__(self, value: Any):
    self._value = value
  def getValue(self) -> Any:
    return self._value
  def setValue(self, value: Any):
    self._value = value

class Column:
  def __init__(self, name: str, dataFormat: str):
    self._name = name
    self._dataFormat = dataFormat # RegEx for the format of data in this Cell
    self._cells = []
  def getName(self) -> str:
    return self._name
  def setName(self, name: str) -> None:
    self._name = name
  def setFormat(self, dataFormat:str) -> None:
    self._dataFormat = dataFormat
  def getFormat(self) -> str:
    return self._dataFormat
  def match(self, text: str) -> bool:
    match: re.Match[str] | None = re.search(self._dataFormat, text)
    return match is not None and match.group() == text
  def getCell(self, index: int) -> Cell:
    return self._cells[index]
  def addCell(self, cell: Cell):
    self._cells.append(cell)
  
class Table:
  def __init__(self, columns: List[Column] = []):
    self._columns = columns
  def getColumns(self) -> List[Column]:
    return self._columns
  def setColumns(self, columns: List[Column]) -> None:
    self._columns = columns
  def addColumn(self, column: Column) -> None:
    return self._columns.append(column)
  def removeColumn(self, column, Column) -> None:
    return self._columns.remove(column)
    
  def getEntry(self, index: int) -> Dict[str, Any]:
    result = {}
    for column in self._columns:
      result[column.getName()] = column.getCell(index).getValue()
    return result

def get_page_contents(page: str) -> List[str]:
  ...

def read_table_file(filename: str) -> Table:
  columns: List[Column] = []
  with open(filename,'r') as f:
    for line in f:
      col_name: str = line.split(":",1)[0].strip()
      col_regex: str = line.split(":",1)[1].strip()
      columns.append(Column(col_name, col_regex))
  table: Table = Table(columns)
  return table

def main() -> int:
  
  # Read the table specifications
  
  table_spec_file: str = ""
  table: Table = Table()
  try:
    table_spec_file = input("Input Table Specification File: ")
    if table_spec_file:
      table = read_table_file(table_spec_file)
  except FileNotFoundError:
    print(f"Could not open table specification. {table_spec_file} does not exist")
    return 1
  except IndexError:
    print(f"The table specification file was malformed.")
    return 2
  else:
    print(f"Table Specifications read successfully")
  
  # Get data from webpage

  url = input("Input Page Reference: ")
  response = requests.get(url)
  if response.status_code != 200:
    print(f"Failed to retrieve content. Status code: {response.status_code}")
    return response.status_code
  soup = BeautifulSoup(response.text, 'html.parser')

  # Parse data

  start_tag: str = "<tr>"

  # Start at specified tag

  # Read as many entries into the table as possible, stop when not able

  body = soup.find("body")
  target_table = None
  if isinstance(body, Tag):
    target_table = body.find(
      "table",
      class_="wikitable sortable mw-datatable sticky-header-multi sort-under plainrowheaders",
      style="text-align: center;"
    )

  rows = []
  if isinstance(target_table, Tag):
    rows = target_table.find_all("tr")
    for i, row in enumerate(rows):
      if isinstance(row, Tag):
        th = row.find("th", {"scope": "row"})
        state_name = None
        if th and isinstance(th, Tag):
          a = th.find("a")
          if a:
            state_name = a.get_text(strip=True)
        if state_name:
          print(f"Row {i} State: {state_name}")
        # Continue with your <td> extraction as before
        data = row.find_all("td")
        for j, d in enumerate(data):
          if isinstance(d, Tag):
            cell_text = d.get_text(strip=True)
            print(f"  Data {j}: {cell_text}")

    

  # with open("soup.out",'w',encoding='utf-8') as f:
  #   if target_table:
  #     f.write(str(target_table))
  #   else:
  #     f.write("Table not found.")

  return 0

if __name__ == "__main__":
  main()