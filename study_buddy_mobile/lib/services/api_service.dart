import 'dart:convert';
import 'package:http/http.dart' as http;
import '../utils/api_base.dart';

class ApiService {
  static Future<List<dynamic>> fetchFlashcards(String topic) async {
    final uri = ApiBase.endpoint("/flashcards?force=true");
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'topic': topic}),
    );
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      return [];
    }
  }

  static Future<String> fetchStudyContent(String topic) async {
    final uri = ApiBase.endpoint("/study_content");
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'topic': topic}),
    );
    if (response.statusCode == 200) {
      return response.body;
    } else {
      return "Error fetching study content";
    }
  }

  static Future<String> fetchQuiz(String topic) async {
    final uri = ApiBase.endpoint("/quiz?force=true");
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'topic': topic}),
    );
    if (response.statusCode == 200) {
      return response.body;
    } else {
      return "Error fetching quiz";
    }
  }

  static Future<String> fetchTest(String topic) async {
    final uri = ApiBase.endpoint("/test?force=true");
    final response = await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'topic': topic}),
    );
    if (response.statusCode == 200) {
      return response.body;
    } else {
      return "Error fetching test";
    }
  }

  static Future<void> sendTopicToAPI(String topic) async {
    final uri = ApiBase.endpoint("/add_topic");
    await http.post(
      uri,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'topic': topic}),
    );
  }

  static Future<List<String>> getTopicsFromAPI() async {
    final uri = ApiBase.endpoint("/get_topics");
    final response = await http.get(uri);
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return List<String>.from(data['topics'] ?? []);
    } else {
      return ["Error fetching topics"];
    }
  }

  static Future<String> loadFromServer(String topic) async {
    List<String> endpoints = ["flashcards", "quiz", "test"];
    String result = "";

    for (String endpoint in endpoints) {
      final uri = ApiBase.endpoint("/$endpoint?topic=$topic");
      try {
        final res = await http.get(uri);
        if (res.statusCode == 200) {
          result += "\n$endpoint:\n${res.body}\n";
        } else {
          result += "\n$endpoint: Error loading\n";
        }
      } catch (e) {
        result += "\n$endpoint: Connection error\n";
      }
    }

    return result;
  }
}
