import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';
import '../config/env.dart';

class ApiBase {
  static String get baseUrl {
    if (kIsWeb) {
      // ✅ In production, this will be "/studybuddy/api"
      return '/studybuddy/api';
    } else if (Platform.isAndroid) {
      return 'http://10.0.2.2:8000/api';
    } else {
      return 'http://$localIp:8000/api';
    }
  }

  static Uri endpoint(String path) {
    return Uri.parse('$baseUrl$path');
  }
}