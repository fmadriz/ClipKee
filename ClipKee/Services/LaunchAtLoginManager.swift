import AppKit
import Foundation
import Observation
import ServiceManagement

@MainActor
@Observable
final class LaunchAtLoginManager {
    private(set) var requiresApproval = false

    private enum Keys {
        static let enabled = "launchAtLoginEnabled"
    }

    var isEnabled: Bool {
        get {
            if UserDefaults.standard.object(forKey: Keys.enabled) == nil {
                return true
            }
            return UserDefaults.standard.bool(forKey: Keys.enabled)
        }
        set {
            UserDefaults.standard.set(newValue, forKey: Keys.enabled)
            applyPreference(enabled: newValue)
        }
    }

    func applyOnLaunch() {
        refreshStatus()

        guard isEnabled else { return }

        let status = SMAppService.mainApp.status
        guard status == .notRegistered || status == .requiresApproval else { return }

        applyPreference(enabled: true)
    }

    func refreshStatus() {
        requiresApproval = SMAppService.mainApp.status == .requiresApproval
        syncPreferenceWithSystemStatus()
    }

    private func syncPreferenceWithSystemStatus() {
        switch SMAppService.mainApp.status {
        case .enabled:
            UserDefaults.standard.set(true, forKey: Keys.enabled)
        case .requiresApproval:
            UserDefaults.standard.set(true, forKey: Keys.enabled)
        case .notRegistered, .notFound:
            if UserDefaults.standard.object(forKey: Keys.enabled) != nil {
                UserDefaults.standard.set(false, forKey: Keys.enabled)
            }
        @unknown default:
            break
        }
    }

    private func applyPreference(enabled: Bool) {
        do {
            if enabled {
                try SMAppService.mainApp.register()
            } else {
                try SMAppService.mainApp.unregister()
            }
        } catch {
            print("Launch at login error: \(error)")
        }

        refreshStatus()
    }

    func openLoginItemsSettings() {
        guard let url = URL(string: "x-apple.systempreferences:com.apple.LoginItems-Settings.extension") else {
            return
        }
        NSWorkspace.shared.open(url)
    }
}
