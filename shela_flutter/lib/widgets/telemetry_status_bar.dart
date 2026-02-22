import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/telemetry_data.dart';

class TelemetryStatusBar extends StatelessWidget {
  final TelemetryData? data;
  const TelemetryStatusBar({super.key, this.data});

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final d = data ?? TelemetryData.initial();
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      color: theme.colorScheme.surfaceContainerHighest,
      child: Row(
        children: [
          Text('${d.agent} (${d.status})', style: GoogleFonts.firaCode(fontSize: 10)),
          const Spacer(),
          Text('${d.usage.tokensTotal} tokens | \$${d.usage.estimatedCost.toStringAsFixed(5)} | ${d.model}', style: GoogleFonts.firaCode(fontSize: 10)),
        ],
      ),
    );
  }
}
