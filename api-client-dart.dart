import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiClient {
  static const String _baseUrl = 'https://qzry3wuxnk.execute-api.eu-north-1.amazonaws.com/';

  static Future<Map<String, dynamic>> summarizeThread(String url) async {
    final response = await http.post(
      Uri.parse('$_baseUrl/summarize'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({'tweet_url': url}),
    );

    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to summarize thread: ${response.body}');
    }
  }
}
