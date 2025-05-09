import 'package:flutter/material.dart';
import 'package:study_buddy_mobile/pages/topic_input_page.dart';
import 'config/env.dart'; // 👈 import it

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  checkEnv(); // 👈 fail early if not set
  runApp(const StudyBuddyApp());
}

class StudyBuddyApp extends StatefulWidget {
  const StudyBuddyApp({super.key});

  @override
  State<StudyBuddyApp> createState() => _StudyBuddyAppState();
}

class _StudyBuddyAppState extends State<StudyBuddyApp> {
  bool isDarkMode = false;

  void toggleTheme() {
    setState(() {
      isDarkMode = !isDarkMode;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Study Buddy',
      themeMode: isDarkMode ? ThemeMode.dark : ThemeMode.light,
      theme: ThemeData(
        brightness: Brightness.light,
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue, brightness: Brightness.dark),
      ),
      home: TopicInputPage(toggleTheme: toggleTheme),
    );
  }
}
