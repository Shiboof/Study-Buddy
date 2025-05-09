// lib/config/env.dart
const String localIp = '192.168.254.105';

void checkEnv() {
  if (localIp.contains("REPLACE")) {
    throw Exception("❌ You must set your local IP in env.dart");
  }
}