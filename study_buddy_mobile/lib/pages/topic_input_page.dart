import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:path_provider/path_provider.dart'; // for mobile/desktop
import 'dart:io'; // for mobile/desktop

import 'package:study_buddy_mobile/utils/file_saver_stub.dart'; // ✅ fixed
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:study_buddy_mobile/pages/flashcard_page.dart';
import 'package:study_buddy_mobile/pages/quiz_test_viewer_page.dart';
import 'package:study_buddy_mobile/services/api_service.dart';

class TopicInputPage extends StatefulWidget {
  final void Function() toggleTheme;
  const TopicInputPage({super.key, required this.toggleTheme});

  @override
  State<TopicInputPage> createState() => _TopicInputPageState();
}

class _TopicInputPageState extends State<TopicInputPage> {
  final TextEditingController _controller = TextEditingController();
  String _studyContent = "";
  String _flashcardContent = "";
  String _quizContent = "";
  String _testContent = "";
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadPersistedData();
  }

  Future<void> _loadPersistedData() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _studyContent = prefs.getString('studyContent') ?? "";
      _flashcardContent = prefs.getString('flashcardContent') ?? "";
      _quizContent = prefs.getString('quizContent') ?? "";
      _testContent = prefs.getString('testContent') ?? "";
    });
  }

  Future<void> _persistData() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('studyContent', _studyContent);
    await prefs.setString('flashcardContent', _flashcardContent);
    await prefs.setString('quizContent', _quizContent);
    await prefs.setString('testContent', _testContent);
  }

  void _clearStudyData() async {
    setState(() {
      _studyContent = "";
      _flashcardContent = "";
      _quizContent = "";
      _testContent = "";
    });
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
  }

  void _downloadStudyData() async {
  final now = DateTime.now();
  final formattedDate = "${now.year}-${now.month.toString().padLeft(2, '0')}-${now.day.toString().padLeft(2, '0')}";
  final fileName = "study_data_$formattedDate.txt";

  final content = '''
📌 Study Notes:
$_studyContent

📌 Flashcards:
$_flashcardContent

📌 Quiz:
$_quizContent

📌 Test:
$_testContent
''';

  try {
    final saver = FileSaver(); // will resolve to WebFileSaver or IOFileSaver automatically
    await saver.saveFile(fileName, content);

    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Saved file: $fileName')),
    );
  } catch (e) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Error saving file: $e')),
    );
  }
}


  // Include all your previous generate methods here
void _generateFlashcards() async {
  if (_controller.text.isEmpty) return;

  setState(() {
    _isLoading = true;
  });

  showDialog(
    context: context,
    barrierDismissible: false,
    builder: (context) => const Center(child: CircularProgressIndicator()),
  );

  try {
    final cards = await ApiService.fetchFlashcards(_controller.text);
    final casted = List<Map<String, dynamic>>.from(cards);
    final asText = casted.map((card) => "Q: ${card['question']}\nA: ${card['answer']}").join("\n\n");

    setState(() {
      _flashcardContent = asText;
      _isLoading = false; // ✅ Move here
    });

    await _persistData();

    if (!mounted) return;
    Navigator.pop(context); // dismiss loading dialog
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => FlashcardPage(
          cards: casted,
          toggleTheme: widget.toggleTheme,
        ),
      ),
    );
  } catch (e) {
    Navigator.pop(context); // dismiss loading dialog
    setState(() {
      _isLoading = false;
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text("Failed to generate flashcards: $e")),
    );
  }
}


  void _generateStudyContent() async {
  if (_controller.text.isEmpty) return;

  setState(() => _isLoading = true);

  showDialog(
    context: context,
    barrierDismissible: false,
    builder: (context) => const Center(child: CircularProgressIndicator()),
  );

  try {
    final content = await ApiService.fetchStudyContent(_controller.text);
    setState(() {
      _studyContent = content;
      _isLoading = false;
    });
    await _persistData();
    if (!mounted) return;
    Navigator.pop(context); // dismiss loading dialog
  } catch (e) {
    Navigator.pop(context); // dismiss loading dialog
    setState(() => _isLoading = false);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text("Failed to generate study content: $e")),
    );
  }
}


  void _generateQuiz() async {
  if (_controller.text.isEmpty) return;

  setState(() => _isLoading = true);

  showDialog(
    context: context,
    barrierDismissible: false,
    builder: (context) => const Center(child: CircularProgressIndicator()),
  );

  try {
    final quiz = await ApiService.fetchQuiz(_controller.text);
    setState(() {
      _quizContent = quiz;
      _isLoading = false;
    });
    await _persistData();
    if (!mounted) return;
    Navigator.pop(context); // dismiss loading dialog
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => QuizTestViewerPage(
          title: "Quiz",
          content: quiz,
          toggleTheme: widget.toggleTheme,
        ),
      ),
    );
  } catch (e) {
    Navigator.pop(context); // dismiss loading dialog
    setState(() => _isLoading = false);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text("Failed to generate quiz: $e")),
    );
  }
}



  void _generateTest() async {
  if (_controller.text.isEmpty) return;

  setState(() => _isLoading = true);

  showDialog(
    context: context,
    barrierDismissible: false,
    builder: (context) => const Center(child: CircularProgressIndicator()),
  );

  try {
    final test = await ApiService.fetchTest(_controller.text);
    setState(() {
      _testContent = test;
      _isLoading = false;
    });
    await _persistData();
    if (!mounted) return;
    Navigator.pop(context); // dismiss loading dialog
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => QuizTestViewerPage(
          title: "Test",
          content: test,
          toggleTheme: widget.toggleTheme,
        ),
      ),
    );
  } catch (e) {
    Navigator.pop(context); // dismiss loading dialog
    setState(() => _isLoading = false);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text("Failed to generate test: $e")),
    );
  }
}



  Widget _buildStudySection(String title, String content) {
    if (content.isEmpty) return const SizedBox.shrink();
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("📌 $title", style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 4),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              border: Border.all(color: Theme.of(context).dividerColor),
              borderRadius: BorderRadius.circular(6),
            ),
            child: SelectableText(content, style: const TextStyle(fontSize: 14)),
          ),
        ],
      ),
    );
  }

  Widget _buildStudyDataBox() {
    final hasData = [_studyContent, _flashcardContent, _quizContent, _testContent].any((c) => c.isNotEmpty);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text("📚 Study Data", style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        const SizedBox(height: 8),
        if (!hasData)
          const Text("No study data generated yet."),
        if (hasData) ...[
          _buildStudySection("Study Notes", _studyContent),
          _buildStudySection("Flashcards", _flashcardContent),
          _buildStudySection("Quiz", _quizContent),
          _buildStudySection("Test", _testContent),
          Align(
            alignment: Alignment.centerRight,
            child: TextButton.icon(
              onPressed: _clearStudyData,
              icon: const Icon(Icons.delete_outline, color: Colors.red),
              label: const Text("Clear All", style: TextStyle(color: Colors.red)),
            ),
          ),
        ]
      ],
    );
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text("Study Buddy"),
        actions: [
          IconButton(
            icon: const Icon(Icons.brightness_6),
            onPressed: widget.toggleTheme,
            tooltip: "Toggle Dark Mode",
          )
        ],
      ),
      body: Container(
        color: colorScheme.surface,
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(controller: _controller, decoration: const InputDecoration(labelText: "Enter Topic")),
            const SizedBox(height: 16),
            Wrap(spacing: 10, runSpacing: 10, children: [
              ElevatedButton(onPressed: _generateStudyContent, child: const Text("Generate Study Content")),
              ElevatedButton(onPressed: _generateFlashcards, child: const Text("Generate Flashcards")),
              ElevatedButton(onPressed: _generateQuiz, child: const Text("Generate Quiz")),
              ElevatedButton(onPressed: _generateTest, child: const Text("Generate Test")),
              ElevatedButton.icon(onPressed: _downloadStudyData, icon: const Icon(Icons.download),label: const Text("Download Content"),
              ),
            ]),
            const SizedBox(height: 20),
            Expanded(child: SingleChildScrollView(child: _buildStudyDataBox())),
          ],
        ),
      ),
    );
  }
}
