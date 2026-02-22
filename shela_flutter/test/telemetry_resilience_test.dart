import 'package:flutter_test/flutter_test.dart';
import 'package:shela_flutter/models/telemetry_data.dart';

void main() {
  test('TelemetryData.fromJson handles empty map', () {
    final data = TelemetryData.fromJson({});
    expect(data.agent, 'unknown');
  });

  test('TelemetryData.initial provides sensible defaults', () {
    final data = TelemetryData.initial();
    expect(data.agent, 'unknown');
    expect(data.status, 'idle');
    expect(data.usage.tokensTotal, 0);
  });
}
