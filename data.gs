function doGet(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("Trang tính1");
  var data = sheet.getDataRange().getValues();
  var headers = data[0];
  var nameIndex = headers.indexOf("Họ và tên");
  var idIndex = headers.indexOf("MSSV");

  if (nameIndex === -1 || idIndex === -1) {
    return ContentService
      .createTextOutput(JSON.stringify({ error: "Columns not found" }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  var rows = [];
  for (var i = 1; i < data.length; i++) {
    rows.push({
      "MSSV": data[i][idIndex],
      "Họ và tên": data[i][nameIndex]
    });
  }

  return ContentService
    .createTextOutput(JSON.stringify(rows))
    .setMimeType(ContentService.MimeType.JSON);
}