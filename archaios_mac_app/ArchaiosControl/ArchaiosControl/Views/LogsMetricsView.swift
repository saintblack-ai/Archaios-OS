// LogsMetricsView.swift
// Displays current log files, selected log content, and formatted metrics JSON.

import SwiftUI

struct LogsMetricsView: View {
    @EnvironmentObject private var state: AppState

    var body: some View {
        VStack(alignment: .leading, spacing: 14) {
            Text("Logs & Metrics Viewer")
                .font(.title2)
                .fontWeight(.semibold)

            HStack(spacing: 10) {
                Button("View Logs") {
                    Task {
                        do {
                            try await state.viewLogs()
                        } catch {
                            state.lastError = error.localizedDescription
                        }
                    }
                }
                .disabled(state.isBusy)

                Button("Show Metrics") { state.loadMetricsButton() }
                    .disabled(state.isBusy)
            }

            if let error = state.lastError {
                Text(error)
                    .foregroundColor(.red)
            }

            HStack(alignment: .top, spacing: 12) {
                GroupBox("Log Files") {
                    List(state.logFiles, id: \.self, selection: Binding(
                        get: { state.selectedLogFile },
                        set: { newValue in
                            guard !newValue.isEmpty else { return }
                            state.selectLog(newValue)
                        }
                    )) { file in
                        Text(file)
                            .font(.system(size: 12, design: .monospaced))
                    }
                    .frame(minWidth: 280, minHeight: 240)
                }

                GroupBox("Selected Log Content") {
                    ScrollView {
                        Text(state.selectedLogContent)
                            .font(.system(size: 12, design: .monospaced))
                            .frame(maxWidth: .infinity, alignment: .leading)
                    }
                    .frame(minWidth: 400, minHeight: 240)
                }
            }

            GroupBox("metrics/metrics.json") {
                ScrollView {
                    Text(prettyJSON(state.rawMetricsJSON))
                        .font(.system(size: 12, design: .monospaced))
                        .frame(maxWidth: .infinity, alignment: .leading)
                }
                .frame(minHeight: 180)
            }

            ConsoleView(entries: state.console)
            Spacer()
        }
        .padding(16)
    }

    private func prettyJSON(_ raw: String) -> String {
        guard let data = raw.data(using: .utf8),
              let object = try? JSONSerialization.jsonObject(with: data),
              let prettyData = try? JSONSerialization.data(withJSONObject: object, options: [.prettyPrinted]),
              let pretty = String(data: prettyData, encoding: .utf8) else {
            return raw
        }
        return pretty
    }
}
