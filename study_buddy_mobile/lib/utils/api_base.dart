import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';
import '../config/env.dart';

class ApiBase {
  static String get baseUrl {
    if (kIsWeb) {
      return 'http://localhost:8080/api'; // Only one /api here
    } else if (Platform.isAndroid) {
      return 'http://10.0.2.2:8000/api';
    } else {
      return 'http://$localIp:8000/api';
    }
  }

  static Uri endpoint(String path) {
    return Uri.parse('$baseUrl$path');  // DO NOT ADD /api AGAIN HERE
  }
}
