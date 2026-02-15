// ArchaiosControlApp.swift
// Entry point for the ArchaiosControl macOS app.

import SwiftUI

@main
struct ArchaiosControlApp: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .frame(minWidth: 1200, minHeight: 760)
        }
    }
}
