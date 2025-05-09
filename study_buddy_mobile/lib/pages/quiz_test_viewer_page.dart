import 'package:flutter/material.dart';

class QuizTestViewerPage extends StatelessWidget {
  final String title;
  final String content;
  final void Function() toggleTheme;

  const QuizTestViewerPage({
    super.key,
    required this.title,
    required this.content,
    required this.toggleTheme,
  });

  List<Widget> _parseQuizContent(BuildContext context) {
    final List<Widget> widgets = [];
    final lines = content.split('\n');

    bool inCodeBlock = false;
    List<String> codeLines = [];

    for (final line in lines) {
      if (line.trim().startsWith('```')) {
        inCodeBlock = !inCodeBlock;

        if (!inCodeBlock && codeLines.isNotEmpty) {
          widgets.add(Container(
            width: double.infinity,
            margin: const EdgeInsets.symmetric(vertical: 8),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surfaceContainerHighest,
              borderRadius: BorderRadius.circular(8),
            ),
            child: SelectableText(
              codeLines.join('\n'),
              style: const TextStyle(fontFamily: 'monospace'),
            ),
          ));
          codeLines.clear();
        }
        continue;
      }

      if (inCodeBlock) {
        codeLines.add(line);
      } else {
          widgets.add(Padding(
            padding: const EdgeInsets.symmetric(vertical: 6.0),
            child: Text(
              line,
              style: const TextStyle(fontSize: 16),
            ),
          ));
        }
    }

    return widgets;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(title),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.brightness_6),
            onPressed: toggleTheme,
            tooltip: "Toggle Dark Mode",
          )
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: _parseQuizContent(context),
          ),
        ),
      ),
    );
  }
}