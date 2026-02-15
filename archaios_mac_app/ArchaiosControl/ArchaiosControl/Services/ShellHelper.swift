// ShellHelper.swift
// Executes shell commands via zsh and captures stdout/stderr asynchronously.

import Foundation

enum ShellHelperError: LocalizedError {
    case nonZeroExit(ShellCommandResult)

    var errorDescription: String? {
        switch self {
        case .nonZeroExit(let result):
            return "Command failed with exit code \(result.exitCode): \(result.command)"
        }
    }

    var result: ShellCommandResult? {
        switch self {
        case .nonZeroExit(let result):
            return result
        }
    }
}

final class ShellHelper {
    func run(command: String, in workingDirectory: String) async throws -> ShellCommandResult {
        try await withCheckedThrowingContinuation { continuation in
            let process = Process()
            let outPipe = Pipe()
            let errPipe = Pipe()

            process.executableURL = URL(fileURLWithPath: "/bin/zsh")
            process.arguments = ["-lc", command]
            process.currentDirectoryURL = URL(fileURLWithPath: workingDirectory)
            process.standardOutput = outPipe
            process.standardError = errPipe

            process.terminationHandler = { proc in
                let outData = outPipe.fileHandleForReading.readDataToEndOfFile()
                let errData = errPipe.fileHandleForReading.readDataToEndOfFile()

                let result = ShellCommandResult(
                    command: command,
                    stdout: String(decoding: outData, as: UTF8.self),
                    stderr: String(decoding: errData, as: UTF8.self),
                    exitCode: proc.terminationStatus
                )

                if proc.terminationStatus == 0 {
                    continuation.resume(returning: result)
                } else {
                    continuation.resume(throwing: ShellHelperError.nonZeroExit(result))
                }
            }

            do {
                try process.run()
            } catch {
                continuation.resume(throwing: error)
            }
        }
    }
}
