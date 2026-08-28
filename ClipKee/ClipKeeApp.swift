import SwiftUI
import AppKit

private enum MenuBarTooltip {
    static func apply(_ text: String, retryCount: Int = 12) {
        DispatchQueue.main.async {
            apply(text, remainingAttempts: retryCount)
        }
    }

    private static func apply(_ text: String, remainingAttempts: Int) {
        if let button = locateMenuBarButton() {
            button.toolTip = text
            return
        }

        guard remainingAttempts > 0 else { return }

        DispatchQueue.main.asyncAfter(deadline: .now() + 0.05) {
            apply(text, remainingAttempts: remainingAttempts - 1)
        }
    }

    private static func locateMenuBarButton() -> NSStatusBarButton? {
        for window in NSApp.windows {
            guard isStatusBarWindow(window) else { continue }
            if let button = findStatusBarButton(in: window.contentView) {
                return button
            }
        }
        return nil
    }

    private static func isStatusBarWindow(_ window: NSWindow) -> Bool {
        String(describing: type(of: window)).contains("StatusBar")
    }

    private static func findStatusBarButton(in view: NSView?) -> NSStatusBarButton? {
        guard let view else { return nil }

        if let button = view as? NSStatusBarButton {
            return button
        }

        for subview in view.subviews {
            if let button = findStatusBarButton(in: subview) {
                return button
            }
        }

        return nil
    }
}

private final class AppDelegate: NSObject, NSApplicationDelegate {
    func applicationDidFinishLaunching(_ notification: Notification) {
        NSApp.setActivationPolicy(.accessory)
        MenuBarTooltip.apply("ClipKee")

        Task { @MainActor in
            LaunchAtLoginManager().applyOnLaunch()
        }
    }
}

@main
struct ClipKeeApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    @State private var store = ClipboardStore()
    @State private var launchAtLoginManager = LaunchAtLoginManager()

    var body: some Scene {
        MenuBarExtra {
            MenuBarRootView()
                .environment(store)
                .environment(launchAtLoginManager)
        } label: {
            Label {
                Text("ClipKee")
            } icon: {
                Image(systemName: "list.clipboard.fill")
                    .font(.system(size: 14, weight: .bold))
                    .accessibilityLabel("ClipKee")
            }
        }
        .menuBarExtraStyle(.window)

        Settings {
            SettingsView(style: .window)
                .environment(launchAtLoginManager)
                .padding(24)
        }
    }
}
