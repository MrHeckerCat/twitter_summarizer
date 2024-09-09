import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:twitter_summarizer/api_client.dart';

class HomePage extends StatefulWidget {
  const HomePage({Key? key}) : super(key: key);

  @override
  _HomePageState createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final TextEditingController _urlController = TextEditingController();
  String _summary = '';
  String _combinedText = '';
  bool _isLoading = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Twitter Thread Summarizer'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _urlController,
              decoration: const InputDecoration(
                labelText: 'Enter Twitter Thread URL',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _isLoading ? null : _summarizeThread,
              child: _isLoading
                  ? const CircularProgressIndicator()
                  : const Text('Summarize'),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: SingleChildScrollView(
                child: Column(
                  children: [
                    _buildExpandableSection('Summary', _summary),
                    const SizedBox(height: 16),
                    _buildExpandableSection('Combined Text', _combinedText),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildExpandableSection(String title, String content) {
    return ExpansionTile(
      title: Text(title),
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text(content),
              const SizedBox(height: 8),
              ElevatedButton(
                onPressed: () => _copyToClipboard(content),
                child: const Text('Copy'),
              ),
            ],
          ),
        ),
      ],
    );
  }

  void _copyToClipboard(String text) {
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Copied to clipboard')),
    );
  }

  Future<void> _summarizeThread() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final result = await ApiClient.summarizeThread(_urlController.text);
      setState(() {
        _summary = result['summary'];
        _combinedText = result['combined_text'];
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${e.toString()}')),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
}
