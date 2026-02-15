// ConsoleView.swift
// Scrollable command console showing command execution output and errors.

import SwiftUI

struct ConsoleView: View {
    let entries: [ConsoleEntry]

    var body: some View {
        GroupBox("Command Console") {
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 6) {
                    ForEach(entries) { entry in
                        Text("[\(time(entry.timestamp))] \(entry.message)")
                            .font(.system(size: 12, weight: .regular, design: .monospaced))
                            .foregroundColor(color(for: entry.level))
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                }
                .padding(.vertical, 6)
            }
            .frame(minHeight: 170)
        }
    }

    private func time(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "HH:mm:ss"
        return formatter.string(from: date)
    }

    private func color(for level: ConsoleEntry.Level) -> Color {
        switch level {
        case .info: return .primary
        case .command: return .blue
        case .output: return .secondary
        case .success: return .green
        case .error: return .red
        }
    }
}
