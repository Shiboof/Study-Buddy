import 'dart:io';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

class FileSaver {
  Future<void> saveFile(String fileName, String content) async {
    try {
      // Get directory (use Downloads for Android, documents for iOS)
      final directory = Platform.isAndroid
          ? await getExternalStorageDirectory()
          : await getApplicationDocumentsDirectory();

      if (directory == null) {
        throw Exception("Cannot access storage directory.");
      }

      final filePath = '${directory.path}/$fileName';
      final file = File(filePath);

      await file.writeAsString(content);

      // Optional: open system share dialog
      await Share.shareXFiles([XFile(file.path)], text: 'Saved file: $fileName');
    } catch (e) {
      throw Exception('Error saving file: $e');
    }
  }
}
