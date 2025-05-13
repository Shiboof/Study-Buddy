// lib/config/env.dart
const String localIp = 'localhost';

void checkEnv() {
  if (localIp.contains("REPLACE")) {
    throw Exception("❌ You must set your local IP in env.dart");
  }
}