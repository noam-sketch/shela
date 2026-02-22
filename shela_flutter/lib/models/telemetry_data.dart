import 'package:flutter/foundation.dart';

@immutable
class UsageData {
  final int tokensIn;
  final int tokensOut;
  final int tokensTotal;
  final double estimatedCost;

  const UsageData({
    this.tokensIn = 0,
    this.tokensOut = 0,
    this.tokensTotal = 0,
    this.estimatedCost = 0.0,
  });

  factory UsageData.fromString(String? usageString) {
    if (usageString == null || usageString.isEmpty) return const UsageData();
    try {
      final tokenRegex = RegExp(r'In (\d+) \| Out (\d+) \| Total (\d+)');
      final costRegex = RegExp(r'Est. Cost: \$([\d.]+)');
      final tokenMatch = tokenRegex.firstMatch(usageString);
      final costMatch = costRegex.firstMatch(usageString);
      return UsageData(
        tokensIn: tokenMatch != null ? int.parse(tokenMatch.group(1)!) : 0,
        tokensOut: tokenMatch != null ? int.parse(tokenMatch.group(2)!) : 0,
        tokensTotal: tokenMatch != null ? int.parse(tokenMatch.group(3)!) : 0,
        estimatedCost: costMatch != null ? double.parse(costMatch.group(1)!) : 0.0,
      );
    } catch (_) { return const UsageData(); }
  }
}

@immutable
class TelemetryData {
  final String agent;
  final String status;
  final UsageData usage;
  final String model;
  final DateTime timestamp;

  const TelemetryData({
    required this.agent,
    required this.status,
    required this.usage,
    required this.model,
    required this.timestamp,
  });

  factory TelemetryData.fromJson(Map<String, dynamic> json) {
    return TelemetryData(
      agent: json['agent'] as String? ?? 'unknown',
      status: json['status'] as String? ?? 'unknown',
      usage: json['usage'] is String 
          ? UsageData.fromString(json['usage'] as String)
          : const UsageData(),
      model: json['model'] as String? ?? 'unknown',
      timestamp: DateTime.fromMillisecondsSinceEpoch(((json['timestamp'] as num? ?? 0) * 1000).toInt()),
    );
  }

  factory TelemetryData.initial() {
    return TelemetryData(
      agent: 'unknown',
      status: 'idle',
      usage: const UsageData(),
      model: 'unknown',
      timestamp: DateTime.now(),
    );
  }
}
