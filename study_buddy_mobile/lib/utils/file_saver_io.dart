import 'dart:io';
import 'package:path_provider/path_provider.dart';

class FileSaver {
  Future<void> saveFile(String fileName, String content) async {
    Directory? targetDir;

    try {
      if (Platform.isAndroid) {
        targetDir = await getExternalStorageDirectory();
      } else if (Platform.isIOS) {
        targetDir = await getApplicationDocumentsDirectory();
      } else if (Platform.isWindows || Platform.isLinux || Platform.isMacOS) {
        targetDir = await getDownloadsDirectory();
      }

      // Fallback to documents directory if none matched
      targetDir ??= await getApplicationDocumentsDirectory();

      final file = File('${targetDir.path}/$fileName');
      await file.writeAsString(content);

      print("✅ File saved to: ${file.path}");
    } catch (e) {
      print("❌ Failed to save file: $e");
      rethrow;
    }
  }
}
