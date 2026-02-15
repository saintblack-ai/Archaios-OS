// AppState.swift
// Central observable state and task orchestration for UI actions and command console updates.

import Foundation
import SwiftUI

@MainActor
final class AppState: ObservableObject {
    @AppStorage("archaios_root") var archaiosRoot: String = "~/Library/Mobile Documents/com~apple~CloudDocs/QX Technology 2019/Archaios OS"

    @Published var metrics: Metrics = .empty
    @Published var rawMetricsJSON: String = "{}"
    @Published var logFiles: [String] = []
    @Published var selectedLogFile: String = ""
    @Published var selectedLogContent: String = ""
    @Published var console: [ConsoleEntry] = []
    @Published var isBusy: Bool = false
    @Published var busyLabel: String = ""
    @Published var lastError: String?

    private let shell = ShellHelper()

    var expandedRootPath: String {
        NSString(string: archaiosRoot).expandingTildeInPath
    }

    func refreshDashboard() {
        Task {
            await runTask(named: "Refresh Dashboard") {
                try await loadMetrics()
                try await viewLogs()
            }
        }
    }

    func runDailyPipeline() {
        Task {
            await runTask(named: "Run Daily Pipeline") {
                let result = try await shell.run(command: "python3 jobs/daily/run_daily.py", in: expandedRootPath)
                appendShellResult(result)
                try await loadMetrics()
                try await viewLogs()
            }
        }
    }

    func pushToGitHub() {
        Task {
            await runTask(named: "Push to GitHub") {
                let add = try await shell.run(command: "git add .", in: expandedRootPath)
                appendShellResult(add)

                let commit = try await shell.run(command: "git commit -m \"update\" || true", in: expandedRootPath)
                appendShellResult(commit)

                let push = try await shell.run(command: "git push", in: expandedRootPath)
                appendShellResult(push)
            }
        }
    }

    func deployCloudflareWorker() {
        Task {
            await runTask(named: "Deploy Cloudflare Worker") {
                let workerDir = URL(fileURLWithPath: expandedRootPath).appendingPathComponent("cloudflare_worker").path
                let deploy = try await shell.run(command: "wrangler deploy", in: workerDir)
                appendShellResult(deploy)
            }
        }
    }

    func viewLogs() async throws {
        let list = try await shell.run(command: "ls -1 logs 2>/dev/null || true", in: expandedRootPath)
        appendShellResult(list)

        logFiles = list.stdout
            .split(separator: "\n")
            .map(String.init)
            .filter { !$0.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty }

        if let first = logFiles.first {
            try await loadLogContent(fileName: first)
        } else {
            selectedLogFile = ""
            selectedLogContent = "No log files found."
        }
    }

    func selectLog(_ fileName: String) {
        Task {
            await runTask(named: "Load Log File") {
                try await loadLogContent(fileName: fileName)
            }
        }
    }

    func loadMetricsButton() {
        Task {
            await runTask(named: "Show Metrics") {
                try await loadMetrics()
            }
        }
    }

    func viewLogsButton() {
        Task {
            await runTask(named: "View Logs") {
                try await viewLogs()
            }
        }
    }

    private func loadMetrics() async throws {
        let result = try await shell.run(command: "cat metrics/metrics.json", in: expandedRootPath)
        appendShellResult(result)

        let raw = result.stdout.trimmingCharacters(in: .whitespacesAndNewlines)
        rawMetricsJSON = raw.isEmpty ? "{}" : raw

        guard let data = rawMetricsJSON.data(using: .utf8) else {
            throw NSError(domain: "ArchaiosControl", code: 1, userInfo: [NSLocalizedDescriptionKey: "Unable to parse metrics bytes"])
        }
        metrics = try JSONDecoder().decode(Metrics.self, from: data)
    }

    private func loadLogContent(fileName: String) async throws {
        selectedLogFile = fileName
        let safeName = fileName.replacingOccurrences(of: "\"", with: "")
        let result = try await shell.run(command: "cat \"logs/\(safeName)\"", in: expandedRootPath)
        appendShellResult(result)
        selectedLogContent = result.stdout.isEmpty ? "(empty)" : result.stdout
    }

    private func runTask(named name: String, operation: @escaping () async throws -> Void) async {
        guard !isBusy else {
            appendConsole("Task already running.", level: .error)
            return
        }

        isBusy = true
        busyLabel = name
        lastError = nil
        appendConsole("Starting: \(name)", level: .info)

        do {
            try await operation()
            appendConsole("Completed: \(name)", level: .success)
        } catch {
            if let shellError = error as? ShellHelperError, let result = shellError.result {
                appendShellResult(result)
            }
            lastError = (error as? LocalizedError)?.errorDescription ?? error.localizedDescription
            appendConsole("Failed: \(name) - \(lastError ?? "Unknown error")", level: .error)
        }

        busyLabel = ""
        isBusy = false
    }

    private func appendShellResult(_ result: ShellCommandResult) {
        appendConsole("$ \(result.command)", level: .command)

        let stdout = result.stdout.trimmingCharacters(in: .whitespacesAndNewlines)
        if !stdout.isEmpty {
            appendConsole(stdout, level: .output)
        }

        let stderr = result.stderr.trimmingCharacters(in: .whitespacesAndNewlines)
        if !stderr.isEmpty {
            appendConsole(stderr, level: .error)
        }

        appendConsole("Exit: \(result.exitCode)", level: result.exitCode == 0 ? .success : .error)
    }

    private func appendConsole(_ message: String, level: ConsoleEntry.Level) {
        console.append(ConsoleEntry(message: message, level: level))
    }
}
