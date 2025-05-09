import 'package:universal_html/html.dart' as html;

class FileSaver {
  Future<void> saveFile(String fileName, String content) async {
    final blob = html.Blob([content]);
    final url = html.Url.createObjectUrlFromBlob(blob);
    final anchor = html.AnchorElement(href: url)
      ..setAttribute('download', fileName)
      ..click();
    html.Url.revokeObjectUrl(url);
  }
}
