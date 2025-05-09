import 'package:flutter/material.dart';

class FlashcardPage extends StatefulWidget {
  final List<Map<String, dynamic>> cards;
  final void Function() toggleTheme;

  const FlashcardPage({
    super.key,
    required this.cards,
    required this.toggleTheme,
  });

  @override
  State<FlashcardPage> createState() => _FlashcardPageState();
}

class _FlashcardPageState extends State<FlashcardPage> {
  int currentIndex = 0;
  late List<Map<String, dynamic>> shuffledCards;
  String? selectedAnswer;
  bool showAnswer = false;

  @override
  void initState() {
    super.initState();
    shuffledCards = List.from(widget.cards)..shuffle();
  }

  void _nextCard() {
    setState(() {
      if (currentIndex < shuffledCards.length - 1) {
        currentIndex++;
        selectedAnswer = null;
        showAnswer = false;
      }
    });
  }

  void _shuffleCards() {
    setState(() {
      shuffledCards.shuffle();
      currentIndex = 0;
      selectedAnswer = null;
      showAnswer = false;
    });
  }

  @override
Widget build(BuildContext context) {
  if (shuffledCards.isEmpty) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Flashcards"),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.brightness_6),
            onPressed: widget.toggleTheme,
            tooltip: "Toggle Dark Mode",
          ),
        ],
      ),
      body: const Center(
        child: Text(
          "❌ No flashcards were generated.\nPlease try a different topic.",
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 18),
        ),
      ),
    );
  }

  final card = shuffledCards[currentIndex];
  final question = card['question'];
  final options = card['options'] as List<dynamic>;
  final correct = card['answer'];

  final colorScheme = Theme.of(context).colorScheme;
  final textTheme = Theme.of(context).textTheme;

  return Scaffold(
    appBar: AppBar(
      title: const Text("Flashcards"),
      leading: IconButton(
        icon: const Icon(Icons.arrow_back),
        onPressed: () => Navigator.pop(context),
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.brightness_6),
          onPressed: widget.toggleTheme,
          tooltip: "Toggle Dark Mode",
        ),
      ],
    ),
    body: Container(
      color: colorScheme.surface,
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            "Q: $question",
            style: textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          ...options.map(
            (option) => ListTile(
              title: Text(
                option,
                style: textTheme.bodyMedium,
              ),
              leading: Radio<String>(
                value: option,
                groupValue: selectedAnswer,
                onChanged: (val) {
                  setState(() {
                    selectedAnswer = val;
                    showAnswer = true;
                  });
                },
              ),
            ),
          ),
          const SizedBox(height: 20),
          if (showAnswer)
            Text(
              selectedAnswer == correct
                  ? "✅ Correct!"
                  : "❌ Incorrect. Correct answer: $correct",
              style: TextStyle(
                color: selectedAnswer == correct
                    ? Colors.green
                    : colorScheme.error,
                fontWeight: FontWeight.bold,
              ),
            ),
          const Spacer(),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              ElevatedButton(
                onPressed: _shuffleCards,
                child: const Text("Shuffle"),
              ),
              ElevatedButton(
                onPressed: _nextCard,
                child: const Text("Next"),
              ),
            ],
          )
        ],
      ),
    ),
  );
}
}
