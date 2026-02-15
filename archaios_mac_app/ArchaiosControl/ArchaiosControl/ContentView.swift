// ContentView.swift
// Main tab navigation for Dashboard, System Control Panel, and Logs & Metrics Viewer.

import SwiftUI

struct ContentView: View {
    var body: some View {
        TabView {
            DashboardView()
                .tabItem {
                    Label("Dashboard", systemImage: "speedometer")
                }

            SystemControlPanelView()
                .tabItem {
                    Label("System Control Panel", systemImage: "switch.2")
                }

            LogsMetricsView()
                .tabItem {
                    Label("Logs & Metrics Viewer", systemImage: "doc.text.magnifyingglass")
                }
        }
    }
}

#Preview {
    ContentView()
        .environmentObject(AppState())
}
