// Models.swift
// Shared model types for metrics, shell command results, and console entries.

import Foundation

struct Metrics: Codable {
    let dailyTasksCompleted: Int
    let musicReleases: Int
    let contentPosts: Int
    let qxUpdates: Int
    let daysActive: Int
    let goalTargetYears: Int

    enum CodingKeys: String, CodingKey {
        case dailyTasksCompleted = "daily_tasks_completed"
        case musicReleases = "music_releases"
        case contentPosts = "content_posts"
        case qxUpdates = "qx_updates"
        case daysActive = "days_active"
        case goalTargetYears = "goal_target_years"
    }

    static let empty = Metrics(
        dailyTasksCompleted: 0,
        musicReleases: 0,
        contentPosts: 0,
        qxUpdates: 0,
        daysActive: 0,
        goalTargetYears: 3
    )

    var progressPercent: Double {
        let totalDays = max(1, goalTargetYears * 365)
        return min(100.0, (Double(daysActive) / Double(totalDays)) * 100.0)
    }
}

struct ConsoleEntry: Identifiable {
    enum Level {
        case info
        case command
        case output
        case success
        case error
    }

    let id = UUID()
    let timestamp = Date()
    let message: String
    let level: Level
}

struct ShellCommandResult {
    let command: String
    let stdout: String
    let stderr: String
    let exitCode: Int32
}
